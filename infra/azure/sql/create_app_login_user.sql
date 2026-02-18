:setvar AppLoginName pecan_app
:setvar AppPassword REPLACE_WITH_SECURE_PASSWORD
:setvar DbName pecan_crm

IF DB_ID('$(DbName)') IS NULL
BEGIN
    RAISERROR('Database $(DbName) does not exist.', 16, 1);
    RETURN;
END

IF NOT EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = '$(AppLoginName)')
BEGIN
    DECLARE @createLogin nvarchar(max) =
        N'CREATE LOGIN [' + '$(AppLoginName)' + N'] WITH PASSWORD = ''' + '$(AppPassword)' + N''';';
    EXEC(@createLogin);
END
GO

USE [$(DbName)];
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = '$(AppLoginName)')
BEGIN
    DECLARE @createUser nvarchar(max) =
        N'CREATE USER [' + '$(AppLoginName)' + N'] FOR LOGIN [' + '$(AppLoginName)' + N'];';
    EXEC(@createUser);
END
GO

-- Minimum role grants for app runtime.
EXEC sp_addrolemember 'db_datareader', '$(AppLoginName)';
EXEC sp_addrolemember 'db_datawriter', '$(AppLoginName)';
GO

-- Explicitly avoid broad admin grants in MVP.
-- Do NOT grant db_owner.