-- ============================================================
-- SQL Queries — Clinic API
-- Entidades: core_patient, core_treatment
-- ============================================================

-- Estructura de las tablas:
--
-- core_patient(id, identification, first_name, last_name, birth_date, created_at)
-- core_treatment(id, patient_id, name, start_date, end_date, status, created_at)
--
-- status puede ser: 'active', 'completed', 'cancelled'
-- ============================================================


-- ------------------------------------------------------------
-- 1. Pacientes que tengan al menos un tratamiento activo
-- ------------------------------------------------------------

-- Opción A: con INNER JOIN + DISTINCT
SELECT DISTINCT p.*
FROM core_patient p
INNER JOIN core_treatment t ON t.patient_id = p.id
WHERE t.status = 'active';

-- Opción B: con EXISTS (más eficiente con grandes volúmenes)
-- EXISTS para en cuanto encuentra el primer match, sin escanear toda la tabla
SELECT p.*
FROM core_patient p
WHERE EXISTS (
    SELECT 1
    FROM core_treatment t
    WHERE t.patient_id = p.id
      AND t.status = 'active'
);


-- ------------------------------------------------------------
-- 2. Pacientes que nunca hayan tenido tratamientos
-- ------------------------------------------------------------

-- Opción A: con LEFT JOIN (las columnas de treatment quedan NULL si no hay match)
SELECT p.*
FROM core_patient p
LEFT JOIN core_treatment t ON t.patient_id = p.id
WHERE t.id IS NULL;

-- Opción B: con NOT EXISTS
SELECT p.*
FROM core_patient p
WHERE NOT EXISTS (
    SELECT 1
    FROM core_treatment t
    WHERE t.patient_id = p.id
);


-- ------------------------------------------------------------
-- 3. Cantidad de tratamientos por paciente
-- ------------------------------------------------------------

-- LEFT JOIN para incluir pacientes con 0 tratamientos
-- COUNT(t.id) devuelve 0 cuando no hay tratamientos (COUNT(NULL) = 0)
SELECT
    p.id,
    p.first_name,
    p.last_name,
    p.identification,
    COUNT(t.id) AS total_tratamientos
FROM core_patient p
LEFT JOIN core_treatment t ON t.patient_id = p.id
GROUP BY p.id, p.first_name, p.last_name, p.identification
ORDER BY total_tratamientos DESC;


-- ------------------------------------------------------------
-- 4. Tratamiento más reciente de cada paciente
-- ------------------------------------------------------------

-- Con CTE + ROW_NUMBER() OVER (PARTITION BY)
-- PARTITION BY reinicia el contador por cada paciente
-- ORDER BY start_date DESC pone el más reciente primero (rn = 1)
WITH tratamientos_ordenados AS (
    SELECT
        t.*,
        ROW_NUMBER() OVER (
            PARTITION BY t.patient_id
            ORDER BY t.start_date DESC
        ) AS rn
    FROM core_treatment t
)
SELECT
    p.id          AS patient_id,
    p.first_name,
    p.last_name,
    t.id          AS treatment_id,
    t.name        AS treatment_name,
    t.start_date,
    t.end_date,
    t.status
FROM core_patient p
INNER JOIN tratamientos_ordenados t ON t.patient_id = p.id
WHERE t.rn = 1;

-- Alternativa sin CTE (subconsulta)
SELECT p.first_name, p.last_name, t.*
FROM core_patient p
INNER JOIN core_treatment t ON t.patient_id = p.id
WHERE t.start_date = (
    SELECT MAX(t2.start_date)
    FROM core_treatment t2
    WHERE t2.patient_id = p.id
);


-- ------------------------------------------------------------
-- 5. Los 10 pacientes con mayor cantidad de tratamientos
-- ------------------------------------------------------------

SELECT
    p.id,
    p.first_name,
    p.last_name,
    p.identification,
    COUNT(t.id) AS total_tratamientos
FROM core_patient p
LEFT JOIN core_treatment t ON t.patient_id = p.id
GROUP BY p.id, p.first_name, p.last_name, p.identification
ORDER BY total_tratamientos DESC
LIMIT 10;
