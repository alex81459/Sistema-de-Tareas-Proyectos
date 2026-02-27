from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.log_auditoria import LogAuditoria
from app.utils import admin_requerido, paginar

auditoria_bp = Blueprint("auditoria", __name__)


@auditoria_bp.route("", methods=["GET"])
@jwt_required()
@admin_requerido
def listar():
    #lista de logs de auditoria con filtros 
    query = LogAuditoria.query

    #filtros
    categoria = request.args.get("categoria")
    if categoria and categoria in LogAuditoria.CATEGORIAS:
        query = query.filter_by(categoria=categoria)

    accion = request.args.get("accion", "").strip()
    if accion:
        query = query.filter(LogAuditoria.accion.ilike(f"%{accion}%"))

    usuario_correo = request.args.get("usuario_correo", "").strip()
    if usuario_correo:
        query = query.filter(LogAuditoria.usuario_correo.ilike(f"%{usuario_correo}%"))

    fecha_desde = request.args.get("fecha_desde")
    if fecha_desde:
        try:
            from datetime import datetime
            desde = datetime.fromisoformat(fecha_desde)
            query = query.filter(LogAuditoria.creado_en >= desde)
        except ValueError:
            pass

    fecha_hasta = request.args.get("fecha_hasta")
    if fecha_hasta:
        try:
            from datetime import datetime
            hasta = datetime.fromisoformat(fecha_hasta)
            query = query.filter(LogAuditoria.creado_en <= hasta)
        except ValueError:
            pass

    direccion_ip = request.args.get("direccion_ip", "").strip()
    if direccion_ip:
        query = query.filter(LogAuditoria.direccion_ip.ilike(f"%{direccion_ip}%"))

    query = query.order_by(LogAuditoria.creado_en.desc())

    pagina = int(request.args.get("pagina", 1))
    tamano = int(request.args.get("tamano_pagina", 25))
    resultado = paginar(query, pagina, tamano)

    resultado["elementos"] = [
        {
            "id": log.id,
            "usuario_id": log.usuario_id,
            "usuario_correo": log.usuario_correo,
            "categoria": log.categoria,
            "accion": log.accion,
            "detalle": log.detalle,
            "entidad_tipo": log.entidad_tipo,
            "entidad_id": log.entidad_id,
            "direccion_ip": log.direccion_ip,
            "agente_usuario": log.agente_usuario,
            "creado_en": log.creado_en.isoformat() if log.creado_en else None,
        }
        for log in resultado["elementos"]
    ]

    return jsonify(resultado), 200


@auditoria_bp.route("/estadisticas", methods=["GET"])
@jwt_required()
@admin_requerido
def estadisticas():
    #estadisticas rapidas del log de auditoria
    total = LogAuditoria.query.count()

    from sqlalchemy import func
    from datetime import datetime, timezone, timedelta

    hace_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    hace_7d = datetime.now(timezone.utc) - timedelta(days=7)

    eventos_24h = LogAuditoria.query.filter(LogAuditoria.creado_en >= hace_24h).count()
    eventos_7d = LogAuditoria.query.filter(LogAuditoria.creado_en >= hace_7d).count()

    logins_fallidos_24h = LogAuditoria.query.filter(
        LogAuditoria.creado_en >= hace_24h,
        LogAuditoria.accion == "login_fallido"
    ).count()

    por_categoria = dict(
        db.session.query(
            LogAuditoria.categoria,
            func.count(LogAuditoria.id)
        ).group_by(LogAuditoria.categoria).all()
    )

    return jsonify({
        "total": total,
        "eventos_24h": eventos_24h,
        "eventos_7d": eventos_7d,
        "logins_fallidos_24h": logins_fallidos_24h,
        "por_categoria": por_categoria,
    }), 200
