from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app import db
from app.models.proyecto import Proyecto
from app.models.tarea import Tarea
from app.models.etiqueta import Etiqueta, tarea_etiquetas
from app.utils import obtener_uid

panel_bp = Blueprint("panel", __name__)


@panel_bp.route("/resumen", methods=["GET"])
@jwt_required()
def resumen():
    uid = obtener_uid()
    hoy = date.today()

    proyectos_ids = db.session.query(Proyecto.id).filter_by(usuario_id=uid).subquery()

    # Conteo por estado
    conteo_estado = (
        db.session.query(Tarea.estado, func.count(Tarea.id))
        .filter(Tarea.proyecto_id.in_(proyectos_ids))
        .group_by(Tarea.estado)
        .all()
    )
    conteo_estado_dict = {estado: conteo for estado, conteo in conteo_estado}

    # Tareas vencidas
    vencidas = (
        Tarea.query.filter(
            Tarea.proyecto_id.in_(proyectos_ids),
            Tarea.estado != "completada",
            Tarea.fecha_vencimiento != None,
            Tarea.fecha_vencimiento < hoy,
        ).count()
    )

    # Próximas a vencer (7 días)
    proximas = (
        Tarea.query.filter(
            Tarea.proyecto_id.in_(proyectos_ids),
            Tarea.estado != "completada",
            Tarea.fecha_vencimiento != None,
            Tarea.fecha_vencimiento >= hoy,
            Tarea.fecha_vencimiento <= hoy + timedelta(days=7),
        ).count()
    )

    # Etiquetas más usadas
    etiquetas_uso = (
        db.session.query(
            Etiqueta.id,
            Etiqueta.nombre,
            Etiqueta.color,
            func.count(tarea_etiquetas.c.tarea_id).label("total"),
        )
        .join(tarea_etiquetas, Etiqueta.id == tarea_etiquetas.c.etiqueta_id)
        .filter(Etiqueta.usuario_id == uid)
        .group_by(Etiqueta.id)
        .order_by(func.count(tarea_etiquetas.c.tarea_id).desc())
        .limit(10)
        .all()
    )

    # Completadas en rango
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    query_completadas = Tarea.query.filter(
        Tarea.proyecto_id.in_(proyectos_ids),
        Tarea.estado == "completada",
    )
    if fecha_desde:
        try:
            query_completadas = query_completadas.filter(
                func.date(Tarea.completado_en) >= date.fromisoformat(fecha_desde)
            )
        except ValueError:
            pass
    if fecha_hasta:
        try:
            query_completadas = query_completadas.filter(
                func.date(Tarea.completado_en) <= date.fromisoformat(fecha_hasta)
            )
        except ValueError:
            pass
    completadas_rango = query_completadas.count()

    # Total proyectos
    total_proyectos = Proyecto.query.filter_by(usuario_id=uid, estado="activo").count()

    return jsonify({
        "conteo_por_estado": conteo_estado_dict,
        "tareas_vencidas": vencidas,
        "proximas_a_vencer": proximas,
        "etiquetas_mas_usadas": [
            {"id": e.id, "nombre": e.nombre, "color": e.color, "total": e.total}
            for e in etiquetas_uso
        ],
        "tareas_completadas_rango": completadas_rango,
        "total_proyectos_activos": total_proyectos,
    }), 200


@panel_bp.route("/estadisticas-graficas", methods=["GET"])
@jwt_required()
def estadisticas_graficas():
    """Devuelve datos formateados para gráficas del dashboard."""
    uid = obtener_uid()
    hoy = date.today()

    proyectos_ids = db.session.query(Proyecto.id).filter_by(usuario_id=uid).subquery()

    # 1. Tareas por prioridad
    conteo_prioridad = (
        db.session.query(Tarea.prioridad, func.count(Tarea.id))
        .filter(Tarea.proyecto_id.in_(proyectos_ids))
        .group_by(Tarea.prioridad)
        .all()
    )
    tareas_por_prioridad = {p: c for p, c in conteo_prioridad}

    # 2. Tareas completadas por semana (últimas 8 semanas)
    completadas_por_semana = []
    for i in range(7, -1, -1):
        inicio = hoy - timedelta(weeks=i+1)
        fin = hoy - timedelta(weeks=i)
        count = Tarea.query.filter(
            Tarea.proyecto_id.in_(proyectos_ids),
            Tarea.estado == "completada",
            Tarea.completado_en != None,
            func.date(Tarea.completado_en) > inicio,
            func.date(Tarea.completado_en) <= fin,
        ).count()
        completadas_por_semana.append({
            "semana": fin.strftime("%d/%m"),
            "total": count,
        })

    # 3. Tareas por proyecto (top 6)
    tareas_por_proyecto = (
        db.session.query(
            Proyecto.nombre,
            func.count(Tarea.id).label("total"),
        )
        .join(Tarea, Proyecto.id == Tarea.proyecto_id)
        .filter(Proyecto.usuario_id == uid)
        .group_by(Proyecto.id)
        .order_by(func.count(Tarea.id).desc())
        .limit(6)
        .all()
    )

    # 4. Tareas creadas vs completadas por semana (últimas 8 semanas)
    creadas_vs_completadas = []
    for i in range(7, -1, -1):
        inicio = hoy - timedelta(weeks=i+1)
        fin = hoy - timedelta(weeks=i)
        creadas = Tarea.query.filter(
            Tarea.proyecto_id.in_(proyectos_ids),
            func.date(Tarea.creado_en) > inicio,
            func.date(Tarea.creado_en) <= fin,
        ).count()
        completadas = Tarea.query.filter(
            Tarea.proyecto_id.in_(proyectos_ids),
            Tarea.estado == "completada",
            Tarea.completado_en != None,
            func.date(Tarea.completado_en) > inicio,
            func.date(Tarea.completado_en) <= fin,
        ).count()
        creadas_vs_completadas.append({
            "semana": fin.strftime("%d/%m"),
            "creadas": creadas,
            "completadas": completadas,
        })

    return jsonify({
        "tareas_por_prioridad": tareas_por_prioridad,
        "completadas_por_semana": completadas_por_semana,
        "tareas_por_proyecto": [
            {"nombre": nombre, "total": total}
            for nombre, total in tareas_por_proyecto
        ],
        "creadas_vs_completadas": creadas_vs_completadas,
    }), 200
