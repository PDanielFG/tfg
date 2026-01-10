-- phpMyAdmin SQL Dump
-- version 4.6.4
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 14-03-2017 a las 09:57:15
-- Versión del servidor: 5.7.14
-- Versión de PHP: 5.6.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bbdd`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `articulos`
--

CREATE TABLE `articulos` (
  `ART_NUM` int(11) NOT NULL,
  `ART_NOM` varchar(20) COLLATE utf8_spanish_ci NOT NULL,
  `ART_PESO` int(11) DEFAULT NULL,
  `ART_COL` varchar(7) COLLATE utf8_spanish_ci DEFAULT NULL,
  `ART_PC` int(11) NOT NULL,
  `ART_PV` int(11) NOT NULL,
  `ART_PRV` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `CLT_NUM` int(11) NOT NULL,
  `CLT_APELL` varchar(25) COLLATE utf8_spanish_ci NOT NULL,
  `CLT_NOM` varchar(20) COLLATE utf8_spanish_ci DEFAULT NULL,
  `CLT_PAIS` varchar(8) COLLATE utf8_spanish_ci DEFAULT NULL,
  `CLT_POB` varchar(20) COLLATE utf8_spanish_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;



--
-- Estructura de tabla para la tabla `pesos`
--

CREATE TABLE `pesos` (
  `PESO_NOM` varchar(9) COLLATE utf8_spanish_ci NOT NULL,
  `PESO_MIN` int(11) NOT NULL,
  `PESO_MAX` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;


--
-- Estructura de tabla para la tabla `proveedores`
--

CREATE TABLE `proveedores` (
  `PRV_NUM` int(11) NOT NULL,
  `PRV_NOM` varchar(25) COLLATE utf8_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;


--
-- Estructura de tabla para la tabla `tiendas`
--

CREATE TABLE `tiendas` (
  `TDA_NUM` int(11) NOT NULL,
  `TDA_POB` varchar(20) COLLATE utf8_spanish_ci NOT NULL,
  `TDA_GER` varchar(25) COLLATE utf8_spanish_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;



--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `VNT_CLT` int(11) NOT NULL,
  `VNT_TDA` int(11) NOT NULL,
  `VNT_ART` int(11) NOT NULL,
  `VNT_CANT` int(11) DEFAULT NULL,
  `VNT_PRECIO` int(11) DEFAULT NULL,
  `VNT_FCH` varchar(6) COLLATE utf8_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;



--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `articulos`
--
ALTER TABLE `articulos`
  ADD PRIMARY KEY (`ART_NUM`),
  ADD KEY `ART_PRV` (`ART_PRV`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`CLT_NUM`);

--
-- Indices de la tabla `pesos`
--
ALTER TABLE `pesos`
  ADD PRIMARY KEY (`PESO_NOM`);

--
-- Indices de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  ADD PRIMARY KEY (`PRV_NUM`);

--
-- Indices de la tabla `tiendas`
--
ALTER TABLE `tiendas`
  ADD PRIMARY KEY (`TDA_NUM`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD KEY `VNT_CLT` (`VNT_CLT`),
  ADD KEY `VNT_TDA` (`VNT_TDA`),
  ADD KEY `VNT_ART` (`VNT_ART`);

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `articulos`
--
ALTER TABLE `articulos`
  ADD CONSTRAINT `articulos_ibfk_1` FOREIGN KEY (`ART_PRV`) REFERENCES `proveedores` (`PRV_NUM`);

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`VNT_CLT`) REFERENCES `clientes` (`CLT_NUM`),
  ADD CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`VNT_TDA`) REFERENCES `tiendas` (`TDA_NUM`),
  ADD CONSTRAINT `ventas_ibfk_3` FOREIGN KEY (`VNT_ART`) REFERENCES `articulos` (`ART_NUM`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;