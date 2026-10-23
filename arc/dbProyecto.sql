DROP DATABASE IF EXISTS dbProyecto;
CREATE DATABASE dbProyecto;
USE dbProyecto;

-- Catalogo de roles para control de permisos basico.
CREATE TABLE roles (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(30) NOT NULL UNIQUE,
  descripcion VARCHAR(150) NULL
);

-- Usuarios que pueden ingresar al sistema.
CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  id_rol INT NOT NULL,
  usuario VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nombre_completo VARCHAR(100) NOT NULL,
  estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_usuarios_roles
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- Catalogo para evitar repetir texto en cada producto.
CREATE TABLE unidades_medida (
  id_unidad INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE,
  abreviatura VARCHAR(15) NULL
);

-- Catalogo para formatos como bolsa, caja, sobre, unidad, etc.
CREATE TABLE presentaciones (
  id_presentacion INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Catalogo principal de productos.
CREATE TABLE productos (
  codigo VARCHAR(20) PRIMARY KEY,
  id_unidad INT NOT NULL,
  id_presentacion INT NOT NULL,
  descripcion VARCHAR(150) NOT NULL,
  imagen_url VARCHAR(500) NULL,
  precio DECIMAL(10, 2) NOT NULL,
  estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  fecha_registro DATE NOT NULL,
  fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT chk_productos_precio
    CHECK (precio >= 0),
  CONSTRAINT fk_productos_unidades
    FOREIGN KEY (id_unidad) REFERENCES unidades_medida(id_unidad),
  CONSTRAINT fk_productos_presentaciones
    FOREIGN KEY (id_presentacion) REFERENCES presentaciones(id_presentacion)
);

-- Historial de entradas y salidas de inventario.
-- ENTRADA suma existencia, SALIDA resta existencia y AJUSTE permite correcciones controladas.
CREATE TABLE inventario_movimientos (
  id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
  codigo_producto VARCHAR(20) NOT NULL,
  id_usuario INT NOT NULL,
  tipo_movimiento ENUM('ENTRADA', 'SALIDA', 'AJUSTE') NOT NULL,
  direccion_ajuste ENUM('SUMA', 'RESTA') NULL,
  cantidad INT NOT NULL,
  fecha DATE NOT NULL,
  observacion VARCHAR(200) NULL,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_inventario_cantidad
    CHECK (cantidad > 0),
  CONSTRAINT chk_inventario_ajuste
    CHECK (
      (tipo_movimiento = 'AJUSTE' AND direccion_ajuste IS NOT NULL)
      OR (tipo_movimiento <> 'AJUSTE' AND direccion_ajuste IS NULL)
    ),
  CONSTRAINT fk_movimientos_productos
    FOREIGN KEY (codigo_producto) REFERENCES productos(codigo),
  CONSTRAINT fk_movimientos_usuarios
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
