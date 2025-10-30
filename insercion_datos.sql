USE bdPracticaC4_1;

INSERT INTO cCalle (DsCalle) VALUES
('16a Calle Sur Poniente'),
('1a Calle Central Poniente'),
('2a Calle Sur Poniente'),
('Arboledas'),
('Arnica'),
('Ave. Eucalipto'),
('Azucena'),
('Bugambilias'),
('Encino'),
('Fresno'),
('Gardenia'),
('Juznajab'),
('Mariposa'),
('Rosas');

INSERT INTO cColon (DsColon) VALUES
('Belisario Dominguez'),
('Arboledas'),
('Blancas Mariposas'),
('Candelaria'),
('Critobal Colón'),
('Fresnillo'),
('Grecia'),
('Guadalupe'),
('Islas'),
('Las Flores'),
('Matamoros'),
('Sabinos'),
('Tenam'),
('Terán'),
('Zapotal');

INSERT INTO cMunicp (DsMunicp) VALUES
('Berriozabal'),
('Centro'),
('Chicomuselo'),
('Ixtepec'),
('La Trinitaria'),
('Las Margaritas'),
('Libertad'),
('Macuspana'),
('Palenque'),
('San Cristobal');

INSERT INTO cNombre (DsNombre) VALUES
('Alexander'),
('Apolinar'),
('Conrado'),
('Elizabeth'),
('Galilea Jaqueline'),
('Guadalupe'),
('Gumaro'),
('Gumercinda'),
('Joel'),
('José Manuel'),
('Juan'),
('Juan Carlos'),
('Moises'),
('Policarpo'),
('Ricardo'),
('Rosalia'),
('Rosario'),
('Trinidad'),
('Yaravi'),
('Yaravi'),
('Arturo'),
('Dante'),
('Genoveva'),
('Panfilo'),
('Caralampio');

INSERT INTO cApellid (DsApellid) VALUES
('Arcos'),
('Alfonzo'),
('Bolton'),
('Calles'),
('Camargo'),
('Castillo'),
('Concepción'),
('Cordova'),
('Dimitrio'),
('Dionisio'),
('Hernandez'),
('Inocencio'),
('Llamas'),
('Lopez'),
('Manchado'),
('Menchaca'),
('Mendez'),
('Mijares'),
('Monzon'),
('Moreno'),
('Moreno'),
('Ortiz'),
('Perez'),
('Ramirez'),
('Rodas'),
('Rosado'),
('Ruedas'),
('Salas'),
('Santis'),
('Santiz'),
('Solano'),
('Sosa'),
('Tarzo'),
('Terán'),
('Urias'),
('Velazco'),
('Velazquez');

CREATE TABLE IF NOT EXISTS `bdPracticaC4_1`.`cRedSoc` (
  `CvRedSoc` INT NOT NULL AUTO_INCREMENT,
  `DsRedSoc` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`CvRedSoc`)
) ENGINE = InnoDB;

INSERT INTO cRedSoc (DsRedSoc) VALUES
('BeReal'),
('Bilibili'),
('Bluesky'),
('Discord'),
('Facebook (Meta)'),
('Flickr'),
('GamerLink'),
('Instagram (Meta)'),
('Kick'),
('LinkedIn'),
('Lunchclub'),
('Mastodon'),
('MeWe'),
('Opportunity'),
('Pinterest'),
('Snapchat'),
('Steam Community'),
('Threads (Meta)'),
('TikTok'),
('Twitch (Amazon)'),
('Vero'),
('VK (VKontakte)'),
('X (antes Twitter)'),
('Xing'),
('YouTube');

ALTER TABLE `bdPracticaC4_1`.`mDtsPerson`
DROP COLUMN `RedSoc`;

ALTER TABLE `bdPracticaC4_1`.`mDtsPerson`
ADD COLUMN `CvRedSoc` INT NOT NULL AFTER `E_mail`;

ALTER TABLE `bdPracticaC4_1`.`mDtsPerson`
ADD INDEX `Fk_Person_RedSoc_idx` (`CvRedSoc` ASC),
ADD CONSTRAINT `Fk_Person_RedSoc`
  FOREIGN KEY (`CvRedSoc`)
  REFERENCES `bdPracticaC4_1`.`cRedSoc` (`CvRedSoc`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

INSERT INTO cPuesto (DsPuesto) VALUES
('Mantenimiento'),
('Intendencia'),
('Programador'),
('Gerente'),
('Secretaria'),
('Ventas'),
('Diseño'),
('Pedidos');

INSERT INTO cDepto (DsDepto) VALUES
('Contabilidad'),
('Bodega'),
('Compras'),
('Computadoras'),
('Electronica'),
('Finanzas'),
('Herramientas'),
('Inventarios'),
('Memorias'),
('Monitores'),
('Movil'),
('Pedidos'),
('Perifericos'),
('Procesadores'),
('Publicidad'),
('Soldadura'),
('Ventas');

INSERT INTO cAficion (DsAficion) VALUES
('Música'),
('Pesca'),
('Baile'),
('Fotografia'),
('Cine'),
('Teatro'),
('Modelado'),
('Lectura'),
('Pintura'),
('Natación');

INSERT INTO cEstado (DsEstado) VALUES
('Chiapas'),
('Campeche'),
('Guerrero'),
('Oaxaca'),
('Tabasco'),
('Yucatán');

INSERT INTO cPais (DsPais) VALUES
('Guatemala'),
('EE.UU.'),
('México');

INSERT INTO CGdoAca (DsGdoAca) VALUES
('Primaria'),
('Secundaria'),
('Preparatoria'),
('Tecnico(a)'),
('Licenciado(a)'),
('Maestria'),
('Doctorado');

INSERT INTO cGenero (DsGenero) VALUES
('Femenino'),
('Masculino');

INSERT INTO cTpPerso (DsTpPerson) VALUES
('Cliente'),
('Proveedor'),
('Empleado');

INSERT INTO cMarca (DsMarca) VALUES
('Seagete'),
('Verbatin'),
('Kinstong'),
('Acer'),
('Truper'),
('Toshiba'),
('Perfect Choice'),
('Grean Leaf'),
('Mac'),
('LG'),
('Epson');

ALTER TABLE `bdPracticaC4_1`.`mDirec`
ADD COLUMN `CodPos` VARCHAR(10) NOT NULL AFTER `CvPais`;

ALTER TABLE `bdPracticaC4_1`.`mDirec`
MODIFY COLUMN `Referencia` VARCHAR(255) NULL;

INSERT INTO mDirec 
(CvCalle, Numero, CvColon, CvMunic, CvEstado, CvPais, CodPos, Referencia) 
VALUES
(1, '120 A', 1, 1, 1, 1, '12345', NULL),
(2, '345', 2, 2, 2, 2, '23456', NULL),
(3, '213 bis', 3, 3, 3, 3, '34567', NULL),
(1, '456', 3, 4, 4, 3, '45678', NULL),  
(2, '395', 3, 5, 5, 1, '56789', NULL),
(4, '342', 2, 6, 6, 3, '67890', NULL),  
(3, '332', 4, 6, 3, 3, '34569', NULL),
(12, '12 A', 14, 5, 5, 1, '12345', NULL),
(10, '12', 13, 6, 2, 2, '23456', NULL),
(8, '13 E', 5, 3, 6, 3, '34567', NULL),
(5, '13', 3, 10, 1, 3, '45678', NULL), 
(14, '234', 6, 4, 4, 3, '56789', NULL),  
(13, '567', 11, 7, 3, 3, '67890', NULL);

ALTER TABLE `bdPracticaC4_1`.`mProduct`
ADD COLUMN `CodBarra` VARCHAR(20) NULL AFTER `CvProduct`;

ALTER TABLE `bdPracticaC4_1`.`mProduct`
MODIFY COLUMN `CvPresent` INT NULL;

ALTER TABLE `bdPracticaC4_1`.`mProduct` 
MODIFY COLUMN `PorOfer` DECIMAL(10,2) NOT NULL;

INSERT INTO mProduct
(CodBarra, Descripc, CvDepto, CvMarca, Cantidad, PcoCto, PcoVta, PorOfer, Stock, CvProved)
VALUES
('09070545', '1 TB', 9, 1, 5, 100, 120, 110, 2, 3),
('09774523', '1 TB', 9, 6, 3, 120, 140, 130, 2, 5),
('98761234', 'Optico', 13, 7, 10, 50, 60, 55, 3, 5),
('12349876', 'Lanix 14" A4', 4, 11, 2, 1200, 1300, 1250, 1, 8),
('45120978', 'Focus 9" i5', 10, 9, 3, 800, 900, 850, 1, 8);

ALTER TABLE `bdPracticaC4_1`.`mDtsPerson`
ADD COLUMN `CURP` VARCHAR(18) NULL AFTER `CvPerson`,
ADD COLUMN `RFCedC` VARCHAR(13) NULL AFTER `CURP`,
ADD COLUMN `NomEmpresa` VARCHAR(100) NULL AFTER `FecNac`,
ADD COLUMN `www` VARCHAR(100) NULL AFTER `NomEmpresa`,
ADD COLUMN `FecEsc` DATE NULL AFTER `www`,
ADD COLUMN `CvAirRom` INT NULL AFTER `CvAficion`;

ALTER TABLE `bdPracticaC4_1`.`mDtsPerson`
MODIFY COLUMN `CvTpPerso` INT NULL;

ALTER TABLE `bdPracticaC4_1`.`mDtsPerson`
MODIFY COLUMN `CvPuesto` INT NULL,
MODIFY COLUMN `CvDepto` INT NULL;

ALTER TABLE `bdPracticaC4_1`.`mDtsPerson`
MODIFY COLUMN `CvGdoAca` INT NULL;

INSERT INTO mDtsPerson
(CURP, RFCedC, CvNombre, CvApePat, CvApeMat, FecNac, NomEmpresa, www, FecEsc, E_mail, CvRedSoc, Edad, CvGdoAca, Telefono, CvGenero, CvPuesto, CvDepto, CvAficion, CvAirRom, CvDirecc)
VALUES
(NULL, NULL, 1, 1, 1, '1995-01-19', NULL, NULL, NULL, 'jmz@prodigy.net.mx', 5, 30, 7, '701 993 156 02', 1, 3, 10, 1, NULL, 3),
(NULL, NULL, 2, 2, 5, '1995-01-19', NULL, NULL, NULL, 'jrm@hotmail.com', 18, 40, 4, '601 963 632 25', 1, NULL, NULL, 9, 3, 6),
(NULL, NULL, 17, 3, 9, '2010-01-15', 'El Chentle', 'www.elchente.com.mx', NULL, 'gma@prodigy.net.mx', 23, 25, NULL, '601 963 632 25', 2, 7, NULL, 8, 2, 4),
(NULL, NULL, 3, 4, 3, '2005-01-09', NULL, NULL, NULL, 'jrm@hotmail.com', 15, 20, NULL, '701 993 156 02', 2, NULL, 4, 7, 1, 2),
(NULL, NULL, 4, 5, 5, '2000-01-06', 'La Coque', 'www.lacoque.com.mx', NULL, 'mji@prodigy.net.mx', 10, -75, 5, '601 963 632 31', 2, NULL, 1, 8, 2, 1),
(NULL, NULL, 3, 9, 10, '1980-01-11', NULL, NULL, NULL, 'jrm@hotmail.com', 8, 45, NULL, '601 963 632 25', 2, 4, NULL, 10, 3, 5),
(NULL, NULL, 5, 3, 9, '1970-01-15', NULL, NULL, NULL, 'mji@prodigy.net.mx', 5, 55, NULL, '601 963 632 31', 1, 1, NULL, 9, 3, 7),
(NULL, NULL, 6, 1, 10, '1950-01-16', 'La Casita', 'www.lacasita.com.mx', NULL, 'mrm@hotmail.com', 18, 65, 5, '601 963 716 34', 1, 5, 3, 1, 2, 3),
(NULL, NULL, 6, 3, 10, '1990-01-06', NULL, NULL, NULL, 'mrm@hotmail.com', 5, 35, NULL, '601 963 257 14', 2, NULL, 4, 2, 1, 4),
(NULL, NULL, 19, 5, 28, '1991-01-19', NULL, NULL, NULL, 'jrm@hotmail.com', 23, 34, NULL, '701 993 156 02', 2, NULL, 3, 10, 1, 7),
(NULL, NULL, 14, 9, 31, '1980-01-11', NULL, NULL, NULL, 'poli@hotmail.com', 15, 45, NULL, '601 963 632 25', 1, NULL, NULL, 9, 3, 8),
(NULL, NULL, 16, 13, 2, '1971-01-16', NULL, NULL, NULL, 'guada@gmail.com', 18, 54, NULL, '601 963 632 25', 2, 3, NULL, 9, 1, 9),
(NULL, NULL, 7, 3, 33, '1982-01-18', 'El Inocente', 'www.elinocente.com.mx', NULL, 'guma@hotmail.com', 8, 43, NULL, '701 993 632 31', 1, NULL, 4, 7, 2, 10),
(NULL, NULL, 8, 12, 34, '2001-01-19', NULL, NULL, NULL, 'gumer@hotmail.com', 5, 32, NULL, '601 963 632 31', 2, NULL, 1, 8, 3, 11),
(NULL, NULL, 20, 7, 10, '2002-01-10', 'La Coqueta', 'www.lacoqueta.com.mx', NULL, 'yarav@hotmail.com', 18, 23, NULL, '601 963 632 25', 2, 4, NULL, 10, 2, 12),
(NULL, NULL, 24, 4, 1, '2002-01-11', NULL, NULL, NULL, 'panfi@prodigy.net.mx', 5, 23, 6, '601 963 632 25', 1, 1, NULL, 9, 3, 13),
(NULL, NULL, 23, 5, 5, '1960-01-16', 'El Hogar', 'www.elhogar.com.mx', NULL, 'geno@hotmail.com', 10, 65, NULL, '601 963 716 34', 1, NULL, 3, 1, 2, 3),
(NULL, NULL, 22, 3, 6, '1990-01-19', NULL, NULL, NULL, 'dante@hotmail.com', 8, 35, NULL, '601 963 257 14', 2, NULL, 4, 2, 1, 4);

INSERT INTO mUsuario 
(CvPerson, `Login`, `Password`, FecIni, FecVen, EdoCta) 
VALUES
(14, 'Gume', 'Gume30Ro04Ndo*', '2025-04-28', '2025-05-28', 'True'),
(1,  'Lampo', 'Cara30Larm04Pio*', '2025-04-28', '2025-05-28', 'True'),
(2,  'NewUser', 'Geno06Veva0525*', '2025-05-06', '2025-05-30', 'True'),
(3,  'DellUser', 'Dian07Tres0525*', '2025-05-07', '2025-05-30', 'True'),
(4,  'UpdUser', 'Artu08Rito0525*', '2025-05-08', '2025-05-30', 'True'),
(5,  'SellUser', 'Panfi09llos0525*', '2025-05-06', '2025-05-30', 'True');
