from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from app import db
from app.models.proyecto import Proyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta, tarea_etiquetas
from app.models.comentario_tarea import ComentarioTarea
from app.models.checklist_tarea import ChecklistTarea
from app.schemas import (
    TareaSchema, TareaCrearSchema, TareaActualizarSchema,
    ComentarioTareaSchema, ComentarioCrearSchema,
    ChecklistTareaSchema, ChecklistCrearSchema,
    RegistroActividadSchema,
)
from app.utils import (
    paginar, verificar_propiedad_proyecto, verificar_propiedad_tarea,
    verificar_propiedad_etiqueta, registrar_actividad, obtener_uid,
    obtener_usuario_actual, escritura_requerida, registrar_log,
)

tareas_bp = Blueprint("tareas", __name__)
tarea_schema = TareaSchema()
tareas_schema = TareaSchema(many=True)
crear_schema = TareaCrearSchema()
actualizar_schema = TareaActualizarSchema()
comentario_schema = ComentarioTareaSchema()
comentarios_schema = ComentarioTareaSchema(many=True)
checklist_schema = ChecklistTareaSchema()
checklists_schema = ChecklistTareaSchema(many=True)
actividad_schema = RegistroActividadSchema(many=True)


@tareas_bp.route("", methods=["GET"])
@jwt_required()
def listar_tareas():
    uid = obtener_uid()
    usuario = obtener_usuario_actual()

    #admin o jefe ven todas las tareas el resto solo las de sus proyectos
    if usuario.puede_ver_todo:
        query = Tarea.query
    else:
        proyectos_ids = db.session.query(Proyecto.id).filter_by(usuario_id=uid).subquery()
        query = Tarea.query.filter(Tarea.proyecto_id.in_(proyectos_ids))

    # ── Filtros ──
    proyecto_id = request.args.get("proyecto_id", type=int)
    if proyecto_id:
        verificar_propiedad_proyecto(proyecto_id, uid)
        query = query.filter_by(proyecto_id=proyecto_id)

    estado = request.args.get("estado")
    if estado and estado in Tarea.ESTADOS_VALIDOS:
        query = query.filter_by(estado=estado)

    prioridad = request.args.get("prioridad")
    if prioridad and prioridad in Tarea.PRIORIDADES_VALIDAS:
        query = query.filter_by(prioridad=prioridad)

    etiquetas_ids = request.args.get("etiquetas_ids")
    if etiquetas_ids:
        ids = [int(x) for x in etiquetas_ids.split(",") if x.isdigit()]
        if ids:
            query = query.filter(Tarea.etiquetas.any(Etiqueta.id.in_(ids)))

    buscar = request.args.get("buscar", "").strip()
    if buscar:
        query = query.filter(
            or_(
                Tarea.titulo.ilike(f"%{buscar}%"),
                Tarea.descripcion.ilike(f"%{buscar}%"),
            )
        )

    vencida = request.args.get("vencida")
    if vencida == "true":
        query = query.filter(
            Tarea.fecha_vencimiento < date.today(),
            Tarea.estado != "completada",
        )

    fecha_desde = request.args.get("fecha_desde")
    if fecha_desde:
        try:
            query = query.filter(Tarea.fecha_vencimiento >= date.fromisoformat(fecha_desde))
        except ValueError:
            pass

    fecha_hasta = request.args.get("fecha_hasta")
    if fecha_hasta:
        try:
            query = query.filter(Tarea.fecha_vencimiento <= date.fromisoformat(fecha_hasta))
        except ValueError:
            pass

    # ── Ordenamiento ──
    ordenar = request.args.get("ordenar_por", "creado_en_desc")
    orden_map = {
        "fecha_vencimiento": Tarea.fecha_vencimiento.asc().nullslast(),
        "fecha_vencimiento_desc": Tarea.fecha_vencimiento.desc().nullslast(),
        "prioridad": Tarea.prioridad.asc(),
        "prioridad_desc": Tarea.prioridad.desc(),
        "creado_en": Tarea.creado_en.asc(),
        "creado_en_desc": Tarea.creado_en.desc(),
        "actualizado_en": Tarea.actualizado_en.asc(),
        "actualizado_en_desc": Tarea.actualizado_en.desc(),
    }
    query = query.order_by(orden_map.get(ordenar, Tarea.creado_en.desc()))

    pagina = request.args.get("pagina", 1, type=int)
    tamano = request.args.get("tamano_pagina", 20, type=int)
    resultado = paginar(query, pagina, tamano)
    resultado["elementos"] = tareas_schema.dump(resultado["elementos"])
    return jsonify(resultado), 200


@tareas_bp.route("", methods=["POST"])
@jwt_required()
@escritura_requerida
def crear_tarea():
    uid = obtener_uid()
    data = request.get_json(silent=True) or {}
    errores = crear_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    verificar_propiedad_proyecto(data["proyecto_id"], uid)

    tarea = Tarea(
        proyecto_id=data["proyecto_id"],
        titulo=data["titulo"].strip(),
        descripcion=data.get("descripcion"),
        estado=data.get("estado", "pendiente"),
        prioridad=data.get("prioridad", "media"),
        fecha_vencimiento=data.get("fecha_vencimiento"),
    )

    # Asignar etiquetas
    ids_etiquetas = data.get("etiquetas_ids", [])
    if ids_etiquetas:
        etiquetas = Etiqueta.query.filter(
            Etiqueta.id.in_(ids_etiquetas),
            Etiqueta.usuario_id == uid,
        ).all()
        tarea.etiquetas = etiquetas

    if tarea.estado == "completada":
        tarea.completar()

    db.session.add(tarea)
    db.session.flush()
    registrar_actividad(tarea.id, uid, "creada")
    registrar_log("tarea", "crear_tarea", f"Tarea '{tarea.titulo}' creada en proyecto {tarea.proyecto_id}", "tarea", tarea.id)
    db.session.commit()
    return jsonify(tarea_schema.dump(tarea)), 201


@tareas_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def obtener_tarea(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    return jsonify(tarea_schema.dump(tarea)), 200


@tareas_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@escritura_requerida
def actualizar_tarea(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)

    data = request.get_json(silent=True) or {}
    errores = actualizar_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    #si cambia de proyecto verificar propiedad
    if "proyecto_id" in data:
        verificar_propiedad_proyecto(data["proyecto_id"], uid)

    campos = ["titulo", "descripcion", "estado", "prioridad", "fecha_vencimiento", "proyecto_id"]
    for campo in campos:
        if campo in data:
            viejo = str(getattr(tarea, campo))
            nuevo = data[campo]
            if campo == "titulo":
                nuevo = nuevo.strip()
            setattr(tarea, campo, nuevo)
            registrar_actividad(tarea.id, uid, f"cambio_{campo}", viejo, str(nuevo))

    if data.get("estado") == "completada" and tarea.completado_en is None:
        tarea.completar()
    elif data.get("estado") and data["estado"] != "completada":
        tarea.completado_en = None

    if "etiquetas_ids" in data:
        etiquetas = Etiqueta.query.filter(
            Etiqueta.id.in_(data["etiquetas_ids"]),
            Etiqueta.usuario_id == uid,
        ).all()
        tarea.etiquetas = etiquetas

    db.session.commit()
    return jsonify(tarea_schema.dump(tarea)), 200


@tareas_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@escritura_requerida
def eliminar_tarea(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    titulo = tarea.titulo
    registrar_log("tarea", "eliminar_tarea", f"Tarea '{titulo}' (ID {id}) eliminada", "tarea", id)
    db.session.delete(tarea)
    db.session.commit()
    return jsonify({"mensaje": "Tarea eliminada"}), 200


@tareas_bp.route("/<int:id>/completar", methods=["POST"])
@jwt_required()
@escritura_requerida
def completar_tarea(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    registrar_actividad(tarea.id, uid, "completada", tarea.estado, "completada")
    registrar_log("tarea", "completar_tarea", f"Tarea '{tarea.titulo}' marcada como completada", "tarea", tarea.id)
    tarea.completar()
    db.session.commit()
    return jsonify(tarea_schema.dump(tarea)), 200


@tareas_bp.route("/<int:id>/reabrir", methods=["POST"])
@jwt_required()
@escritura_requerida
def reabrir_tarea(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    registrar_actividad(tarea.id, uid, "reabierta", tarea.estado, "pendiente")
    tarea.reabrir()
    db.session.commit()
    return jsonify(tarea_schema.dump(tarea)), 200


#comentarios
@tareas_bp.route("/<int:id>/comentarios", methods=["GET"])
@jwt_required()
def listar_comentarios(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    comentarios = tarea.comentarios.order_by(ComentarioTarea.creado_en.desc()).all()
    return jsonify(comentarios_schema.dump(comentarios)), 200


@tareas_bp.route("/<int:id>/comentarios", methods=["POST"])
@jwt_required()
@escritura_requerida
def crear_comentario(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    data = request.get_json(silent=True) or {}
    errores = ComentarioCrearSchema().validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    comentario = ComentarioTarea(
        tarea_id=tarea.id,
        usuario_id=uid,
        contenido=data["contenido"].strip(),
    )
    db.session.add(comentario)
    registrar_actividad(tarea.id, uid, "comentario_agregado")
    db.session.commit()
    return jsonify(comentario_schema.dump(comentario)), 201


#checklist
@tareas_bp.route("/<int:id>/checklist", methods=["GET"])
@jwt_required()
def listar_checklist(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    items = tarea.checklist.order_by(ChecklistTarea.creado_en.asc()).all()
    return jsonify(checklists_schema.dump(items)), 200


@tareas_bp.route("/<int:id>/checklist", methods=["POST"])
@jwt_required()
@escritura_requerida
def crear_checklist_item(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    data = request.get_json(silent=True) or {}
    errores = ChecklistCrearSchema().validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    item = ChecklistTarea(
        tarea_id=tarea.id,
        descripcion=data["descripcion"].strip(),
        esta_completado=data.get("esta_completado", False),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(checklist_schema.dump(item)), 201


@tareas_bp.route("/<int:tarea_id>/checklist/<int:item_id>", methods=["PUT"])
@jwt_required()
@escritura_requerida
def actualizar_checklist_item(tarea_id, item_id):
    uid = obtener_uid()
    verificar_propiedad_tarea(tarea_id, uid)
    item = ChecklistTarea.query.filter_by(id=item_id, tarea_id=tarea_id).first_or_404()
    data = request.get_json(silent=True) or {}
    if "descripcion" in data:
        item.descripcion = data["descripcion"].strip()
    if "esta_completado" in data:
        item.esta_completado = bool(data["esta_completado"])
    db.session.commit()
    return jsonify(checklist_schema.dump(item)), 200


@tareas_bp.route("/<int:tarea_id>/checklist/<int:item_id>", methods=["DELETE"])
@jwt_required()
@escritura_requerida
def eliminar_checklist_item(tarea_id, item_id):
    uid = obtener_uid()
    verificar_propiedad_tarea(tarea_id, uid)
    item = ChecklistTarea.query.filter_by(id=item_id, tarea_id=tarea_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"mensaje": "Item eliminado"}), 200


#actividad
@tareas_bp.route("/<int:id>/actividad", methods=["GET"])
@jwt_required()
def listar_actividad(id):
    uid = obtener_uid()
    tarea = verificar_propiedad_tarea(id, uid)
    from app.models.registro_actividad import RegistroActividad
    registros = tarea.actividad.order_by(RegistroActividad.creado_en.desc()).all()
    return jsonify(actividad_schema.dump(registros)), 200


#recordatorio
@tareas_bp.route("/recordatorios", methods=["GET"])
@jwt_required()
def recordatorios():
    uid = obtener_uid()
    usuario = obtener_usuario_actual()
    dias = request.args.get("dias", 1, type=int)
    hoy = date.today()
    limite = hoy + timedelta(days=dias)

    if usuario.puede_ver_todo:
        tareas = Tarea.query.filter(
            Tarea.estado != "completada",
            Tarea.fecha_vencimiento != None,
            Tarea.fecha_vencimiento <= limite,
        ).order_by(Tarea.fecha_vencimiento.asc()).all()
    else:
        proyectos_ids = db.session.query(Proyecto.id).filter_by(usuario_id=uid).subquery()
        tareas = Tarea.query.filter(
            Tarea.proyecto_id.in_(proyectos_ids),
            Tarea.estado != "completada",
            Tarea.fecha_vencimiento != None,
            Tarea.fecha_vencimiento <= limite,
        ).order_by(Tarea.fecha_vencimiento.asc()).all()

    return jsonify(tareas_schema.dump(tareas)), 200


#exportar a excel
@tareas_bp.route("/exportar.xlsx", methods=["GET"])
@jwt_required()
def exportar_excel():
    uid = obtener_uid()
    usuario = obtener_usuario_actual()
    from openpyxl import Workbook

    if usuario.puede_ver_todo:
        tareas = Tarea.query.order_by(Tarea.creado_en.desc()).all()
    else:
        proyectos_ids = db.session.query(Proyecto.id).filter_by(usuario_id=uid).subquery()
        tareas = Tarea.query.filter(Tarea.proyecto_id.in_(proyectos_ids)).order_by(Tarea.creado_en.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Tareas"
    ws.append(["ID", "Proyecto", "Título", "Estado", "Prioridad", "Fecha Vencimiento", "Completado En", "Vencida"])

    for t in tareas:
        ws.append([
            t.id,
            t.proyecto.nombre,
            t.titulo,
            t.estado,
            t.prioridad,
            str(t.fecha_vencimiento) if t.fecha_vencimiento else "",
            str(t.completado_en) if t.completado_en else "",
            "Sí" if t.esta_vencida else "No",
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="tareas.xlsx",
    )
