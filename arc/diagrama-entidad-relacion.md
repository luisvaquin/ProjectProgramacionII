# Diagrama Entidad-Relacion - dbProyecto

```mermaid
erDiagram
    ROLES ||--o{ USUARIOS : asigna
    UNIDADES_MEDIDA ||--o{ PRODUCTOS : clasifica
    PRESENTACIONES ||--o{ PRODUCTOS : define
    USUARIOS ||--o{ INVENTARIO_MOVIMIENTOS : registra
    PRODUCTOS ||--o{ INVENTARIO_MOVIMIENTOS : tiene

    ROLES {
        INT id_rol PK
        VARCHAR nombre UK
        VARCHAR descripcion
    }

    USUARIOS {
        INT id_usuario PK
        INT id_rol FK
        VARCHAR usuario UK
        VARCHAR password_hash
        VARCHAR nombre_completo
        ENUM estado
        DATETIME fecha_creacion
        DATETIME fecha_actualizacion
    }

    UNIDADES_MEDIDA {
        INT id_unidad PK
        VARCHAR nombre UK
        VARCHAR abreviatura
    }

    PRESENTACIONES {
        INT id_presentacion PK
        VARCHAR nombre UK
    }

    PRODUCTOS {
        VARCHAR codigo PK
        INT id_unidad FK
        INT id_presentacion FK
        VARCHAR descripcion
        VARCHAR imagen_url
        DECIMAL precio
        ENUM estado
        DATE fecha_registro
        DATETIME fecha_actualizacion
    }

    INVENTARIO_MOVIMIENTOS {
        INT id_movimiento PK
        VARCHAR codigo_producto FK
        INT id_usuario FK
        ENUM tipo_movimiento
        ENUM direccion_ajuste
        INT cantidad
        DATE fecha
        VARCHAR observacion
        DATETIME fecha_creacion
    }
```

## Lectura de las relaciones

- Un rol puede estar asignado a muchos usuarios, pero cada usuario tiene un solo rol.
- Una unidad de medida puede usarse en muchos productos, pero cada producto tiene una sola unidad de medida.
- Una presentacion puede usarse en muchos productos, pero cada producto tiene una sola presentacion.
- Un usuario puede registrar muchos movimientos de inventario, pero cada movimiento lo registra un solo usuario.
- Un producto puede tener muchos movimientos de inventario, pero cada movimiento pertenece a un solo producto.

## Flujo principal

```text
Rol -> Usuario -> Movimiento de inventario <- Producto
                              ^
                              |
                 Unidad de medida + Presentacion
```

Los movimientos `ENTRADA` aumentan existencia (por ejemplo, un reabastecimiento) y los movimientos `SALIDA` la disminuyen (por ejemplo, una venta). Un `AJUSTE` siempre indica su dirección: `SUMA` o `RESTA`. La cantidad actual de un producto se obtiene sumando entradas y ajustes `SUMA`, y restando salidas y ajustes `RESTA`.
