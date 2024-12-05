DELETE FROM [db_conteo_entero].[dbo].[ConteoProductos];
DBCC CHECKIDENT ('ConteoProductos', RESEED, 0);