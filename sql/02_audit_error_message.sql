ALTER TABLE audit.etl_run ADD COLUMN IF NOT EXISTS error_message TEXT;

-- La ejecución 1 quedó colgada; la marcamos para que el historial sea honesto
UPDATE audit.etl_run
SET status = 'FAILED', finished_at = now(),
    error_message = 'Abortada: faltaba la columna error_message en audit.etl_run'
WHERE run_id = 1 AND status = 'RUNNING';