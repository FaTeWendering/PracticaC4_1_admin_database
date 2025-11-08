-- -----------------------------------------------------
-- Script de Inserción para bdPracticaC4_1
-- Adaptado para Proyecto Escuela de Música
-- -----------------------------------------------------
USE bdPracticaC4_1;

-- -----------------------------------------------------
-- 1. CATÁLOGOS BÁSICOS (Datos de Personas)
-- -----------------------------------------------------

-- Insertamos nombres
INSERT INTO cNombre (DsNombre) VALUES
('Pedro'), ('Juanita'), ('Alan'), ('Rivaldo'), ('Rosalia');

-- Insertamos apellidos
INSERT INTO cApellid (DsApellid) VALUES
('Alcoles'), ('Banana'), ('Hernández'), ('Pérez'), ('Llamas');

-- Insertamos géneros
INSERT INTO cGenero (DsGenero) VALUES ('Masculino'), ('Femenino');

-- (BORRAMOS LOS DATOS ANTERIORES DE cTpPerso SI EXISTEN)
DELETE FROM cTpPerso;

-- ADAPTACIÓN: Insertamos los Tipos de Persona del proyecto
INSERT INTO cTpPerso (DsTpPerson) VALUES 
('Administrativo'), -- ID: 1 (depende del autoincrement)
('Profesor'),       -- ID: 2
('Alumno');         -- ID: 3

-- Insertamos puestos
DELETE FROM cPuesto;
INSERT INTO cPuesto (DsPuesto) VALUES 
('Director'),       -- ID: 1
('Profesor'),       -- ID: 2
('Estudiante');     -- ID: 3

-- Insertamos datos genéricos para llenar campos NOT NULL
INSERT INTO cCalle (DsCalle) VALUES ('Calle Principal 123');
INSERT INTO cColon (DsColon) VALUES ('Colonia Centro');
INSERT INTO cMunicp (DsMunicp) VALUES ('Comitán');
INSERT INTO cEstado (DsEstado) VALUES ('Chiapas');
INSERT INTO cPais (DsPais) VALUES ('México');
INSERT INTO CGdoAca (DsGdoAca) VALUES ('Licenciatura');
INSERT INTO cAficion (DsAficion) VALUES ('Música');
INSERT INTO cDepto (DsDepto) VALUES ('Académico');

-- -----------------------------------------------------
-- 2. DATOS MAESTROS
-- -----------------------------------------------------

-- Insertamos una dirección genérica
INSERT INTO mDirec (Numero, CvCalle, CvColon, CvMunic, CvEstado, CvPais, Referencia) VALUES
('123', 1, 1, 1, 1, 1, 'Cerca del parque'); -- ID: 1

-- Insertamos las 4 personas
-- (Asumimos que los IDs de catálogos son 1 para todo, excepto los IDs específicos)

-- Persona 1: Admin (Director)
INSERT INTO mDtsPerson (CvNombre, CvApePat, CvApeMat, FecNac, E_mail, RedSoc, Edad, CvGdoAca, Telefono, CvGenero, CvPuesto, CvDepto, CvAficion, CvDirecc, CvTpPerso) VALUES
(1, 1, 1, '1980-01-01', 'pedro@correo.com', 'N/A', 45, 1, '9630000001', 1, 1, 1, 1, 1, 1); -- ID Persona: 1

-- Persona 2: Profesor
INSERT INTO mDtsPerson (CvNombre, CvApePat, CvApeMat, FecNac, E_mail, RedSoc, Edad, CvGdoAca, Telefono, CvGenero, CvPuesto, CvDepto, CvAficion, CvDirecc, CvTpPerso) VALUES
(2, 2, 2, '1990-05-10', 'juanita@correo.com', 'N/A', 35, 1, '9630000002', 2, 2, 1, 1, 1, 2); -- ID Persona: 2

-- Persona 3: Alumno 1
INSERT INTO mDtsPerson (CvNombre, CvApePat, CvApeMat, FecNac, E_mail, RedSoc, Edad, CvGdoAca, Telefono, CvGenero, CvPuesto, CvDepto, CvAficion, CvDirecc, CvTpPerso) VALUES
(3, 3, 3, '2000-02-15', 'alan@correo.com', 'N/A', 25, 1, '9630000003', 1, 3, 1, 1, 1, 3); -- ID Persona: 3

-- Persona 4: Alumno 2
INSERT INTO mDtsPerson (CvNombre, CvApePat, CvApeMat, FecNac, E_mail, RedSoc, Edad, CvGdoAca, Telefono, CvGenero, CvPuesto, CvDepto, CvAficion, CvDirecc, CvTpPerso) VALUES
(4, 4, 4, '2002-03-20', 'rivaldo@correo.com', 'N/A', 23, 1, '9630000004', 1, 3, 1, 1, 1, 3); -- ID Persona: 4

-- Persona 5: Usuario de prueba (Rosalia Llamas Alfonzo)
INSERT INTO mDtsPerson (CvNombre, CvApePat, CvApeMat, FecNac, E_mail, RedSoc, Edad, CvGdoAca, Telefono, CvGenero, CvPuesto, CvDepto, CvAficion, CvDirecc, CvTpPerso) VALUES
(5, 5, 2, '1995-01-01', 'rosalia@correo.com', 'N/A', 30, 1, '9630000005', 2, 1, 1, 1, 1, 1); -- ID Persona: 5

-- -----------------------------------------------------
-- 3. USUARIOS (Depende de mDtsPerson)
-- -----------------------------------------------------
-- (Las contraseñas cumplen los criterios: 4-10, Mayús, Minús, Num, Especial)
-- (IDs de CvPerson coinciden con los inserts de arriba)

INSERT INTO mUsuario (CvPerson, `Login`, `Password`, FecIni, FecVen, EdoCta) VALUES
(1, 'director', 'Admin123*', '2025-01-01', '2026-01-01', 'True'), -- ID Usuario: 1
(2, 'jbanana', 'Profe456#', '2025-01-01', '2026-01-01', 'True'), -- ID Usuario: 2
(3, 'alan', 'Alumno789+', '2025-01-01', '2026-01-01', 'True'), -- ID Usuario: 3
(4, 'rivaldo', 'Alumno101%', '2025-01-01', '2026-01-01', 'True'), -- ID Usuario: 4
(5, 'rllamas', 'Rossa123#', '2025-01-01', '2026-01-01', 'True'); -- ID Usuario: 5

-- -----------------------------------------------------
-- 4. TABLAS DEL PROYECTO (Depende de mUsuario y cClases)
-- -----------------------------------------------------

-- Insertamos Clases (Asignadas al CvUser 2, 'jbanana')
INSERT INTO cClases (DsClase, CvProfesor, Aula, Hora) VALUES
('Percusión Nivel 1', 2, 'Salón A', '16:00:00'), -- ID Clase: 1
('Teoría Musical', 2, 'Salón B', '18:00:00');    -- ID Clase: 2

-- Insertamos Cobros (Asignados a los CvUser 3 y 4)
INSERT INTO fCobro (CvUsuario, FechaCobro, `Tipo`, Monto, Descuento, Estado) VALUES
(3, '2025-10-01', 'Inscripción', 500.00, 0.00, 'Pagado'),
(4, '2025-11-01', 'Mensualidad', 300.00, 0.00, 'Pendiente');

-- Insertamos Asistencias (Usuarios 3 y 4 en Clase 1)
INSERT INTO eAsistencia (CvClase, CvUsuario, FechaAsistencia, Estado) VALUES
(1, 3, '2025-11-03', 'Asistió'),
(1, 4, '2025-11-03', 'Falta');

-- Insertamos Evaluaciones (Usuario 3 en Clase 1)
INSERT INTO tEvaluacion (CvUsuario, CvClase, Nota, Comentarios) VALUES
(3, 1, 9.5, 'Excelente participación en clase.');