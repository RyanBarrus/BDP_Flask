CREATE SCHEMA validation
CREATE SCHEMA users
CREATE SCHEMA DATA


CREATE TABLE [users].[Login](
	[UserID] [INT] PRIMARY KEY IDENTITY(1,1),
	[UserName] [VARCHAR](99) NOT NULL,
	[HashedPassword] [NVARCHAR](MAX) NULL
)


CREATE TABLE [users].[Permissions](
	[PermissionID] INT PRIMARY KEY IDENTITY(1,1),
	[PermissionName] [VARCHAR](99) NULL
) ON [PRIMARY]
GO




CREATE TABLE [users].[PermissionsAssignment](
	[PermissionAssignmentID] INT PRIMARY KEY IDENTITY(1,1),
	[UserID] INT NOT NULL,
	[PermissionID] INT NOT NULL,
	CONSTRAINT [FK_PermissionAssignment_Login_UserID] FOREIGN KEY (UserID) REFERENCES users.login (UserID) ON DELETE CASCADE,
	CONSTRAINT [FK_PermissionAssignment_Permissions_PermissionID] FOREIGN KEY (PermissionID) REFERENCES users.Permissions (PermissionID) ON DELETE CASCADE
)


CREATE TABLE [users].[PermissionsAssignmentStaging](
	[PermissionStagingAssignmentID] INT PRIMARY KEY IDENTITY(1,1),
	[UserID] INT NOT NULL,
	[PermissionID] INT NOT NULL,
	CONSTRAINT [FK_PermissionAssignmentStaging_Login_UserID] FOREIGN KEY (UserID) REFERENCES users.login (UserID) ON DELETE CASCADE,
	CONSTRAINT [FK_PermissionAssignmentStaging_Permissions_PermissionID] FOREIGN KEY (PermissionID) REFERENCES users.Permissions (PermissionID) ON DELETE CASCADE
)

CREATE TABLE [users].[PermissionsDefaults](
	[PermissionDefaultID] INT PRIMARY KEY IDENTITY(1,1),
	[PermissionID] INT NOT NULL,
	CONSTRAINT [FK_PermissionDefault_Permissions_PermissionID] FOREIGN KEY (PermissionID) REFERENCES users.Permissions (PermissionID) ON DELETE CASCADE
)


CREATE TABLE [data].[pallets](
	[ItemNumber] [VARCHAR](30) NOT NULL,
	[CaseBarcode] [VARCHAR](10) PRIMARY KEY,
	[Pallet] [char](20) NOT NULL,
	[Shift] CHAR(1) NULL,
	[Timestamp] [DATETIME2](7) NOT NULL,
	[UploadUsername] VARCHAR(99)
)


CREATE TABLE data.shipments (
	[SalesOrderNumber] [varchar](30) NULL,
    [Pallet] [char](20) PRIMARY KEY CLUSTERED,
    [Quantity] [numeric](9, 2) NULL,
    [Timestamp] [datetime2](7) NULL,
    [UploadUsername] [varchar](99) NULL,

)



CREATE TABLE [validation].[PalletItemList](
	[PalletItemListID] INT PRIMARY KEY IDENTITY(1,1),
	[ItemNumber] [VARCHAR](999) NULL
) 


CREATE TABLE [validation].[RangeItemList](
	[RangeItemListID] INT PRIMARY KEY IDENTITY(1,1),
	[ItemNumber] [VARCHAR](999) NULL
) 

CREATE TABLE [validation].[AutoItemList](
	[AutoItemListID] INT PRIMARY KEY IDENTITY(1,1),
	[ItemNumber] [VARCHAR](999) NULL
) 

CREATE TABLE [validation].[PalletCount] (
	[ItemNumber] VARCHAR(999),
	[RequiredCount] INT
)

CREATE TABLE [validation].[PalletCountStaging] (
	[ItemNumber] VARCHAR(999),
	[RequiredCount] INT
)



CREATE PROCEDURE [users].[CreateUserIfNotExists]
(
    @UserName VARCHAR(99),
	@HashedPassword NVARCHAR(MAX)
)
AS
BEGIN
	SET NOCOUNT ON

    IF (SELECT 1 FROM users.login WHERE username = @UserName) = 1
	BEGIN
		SELECT 0 AS Result
		RETURN
	END
	
	INSERT INTO users.login (UserName,HashedPassword) VALUES
	(@UserName,@HashedPassword)

	INSERT INTO users.PermissionsAssignment (UserID,PermissionID)
	SELECT SCOPE_IDENTITY() AS UserID,
	perm.PermissionID

	FROM users.PermissionsDefaults perm

	SELECT 1 AS Result
	RETURN
END


CREATE PROCEDURE [users].[DefaultPermissions]
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

	SELECT perm.PermissionId,
	perm.PermissionName,
	CASE WHEN def.PermissionID IS NOT NULL THEN 1 ELSE 0 END AS HasPermission

	FROM users.Permissions perm

	LEFT OUTER JOIN users.PermissionsDefaults def
	ON perm.PermissionID = def.PermissionID

END





CREATE PROCEDURE [users].[PermissionsForUser]
(
    @UserID VARCHAR(99)
)
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

	SELECT perm.PermissionID,
	perm.PermissionName,
	CASE WHEN pass.PermissionID IS NOT NULL THEN 1 ELSE 0 END AS HasPermission

	FROM users.Permissions perm

	LEFT OUTER JOIN users.PermissionsAssignment pass
	ON perm.PermissionID = pass.PermissionID
	AND pass.UserID = @UserID

END


ALTER PROCEDURE [users].[UpdatePermissionsForUser]

AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON


	DELETE 
	FROM [users].[PermissionsAssignment] 
	WHERE UserId = (
		SELECT TOP 1 UserID FROM [users].[PermissionsAssignmentStaging]
		)


	INSERT INTO [users].[PermissionsAssignment] 
	SELECT UserID,PermissionID FROM users.PermissionsAssignmentStaging

	TRUNCATE TABLE [users].[PermissionsAssignmentStaging]

END



CREATE PROCEDURE [users].[UpdateDefaultPermissions]

AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

	DELETE FROM [Users].PermissionsDefaults



	INSERT INTO [Users].PermissionsDefaults
	SELECT PermissionID FROM users.PermissionsAssignmentStaging

	TRUNCATE TABLE [users].[PermissionsAssignmentStaging]

END




CREATE PROCEDURE [validation].[UpdatePalletCount]

AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

	MERGE [validation].[PalletCount] AS target
	USING (

		SELECT ItemNumber,
		RequiredCount
		
		FROM [validation].[PalletCountStaging]

		) AS source 
	ON (target.ItemNumber = source.ItemNumber)
	WHEN MATCHED THEN
		UPDATE SET
			target.RequiredCount = source.RequiredCount

	WHEN NOT MATCHED BY TARGET THEN
		INSERT 
		VALUES (
			source.ItemNumber,
			source.RequiredCount
		)
	WHEN NOT MATCHED BY SOURCE THEN
		DELETE;

	TRUNCATE TABLE [validation].PalletCountStaging

END




GO
CREATE VIEW [data].[ViewPallets] AS
SELECT Pallet, MAX(Timestamp) AS timestamp

FROM [data].[pallets]

GROUP BY Pallet

GO
CREATE VIEW [data].[ViewShipments] AS
SELECT SalesOrderNumber, MAX(Timestamp) AS timestamp

FROM [data].[shipments]

GROUP BY SalesOrderNumber





INSERT INTO users.Permissions VALUES
('/user/create'),
('/user/delete'),
('/user/permissions'),
('/pallets/upload'),
('/pallets/range'),
('/pallets/auto'),
('/pallets/delete'),
('/salesorder/upload'),
('/salesorder/delete'),
('/validation/palletitem'),
('/validation/autoitem'),
('/validation/rangeitem'),
('/validation/palletcount')





INSERT INTO validation.PalletItemList VALUES
('021-FG 10.25 BLUE SPOON STRAW'),
('021-FG BIOSTRAW 7200 GREEN'),
('021-FG TEAL AMERCARE STRAW'),
('021-FG-10.25 SHEETZ RED'),
('021-FG-7.75 WHITE W/RED STRAW'),
('021-FG-8.75" PURPLE WRAP STRAW'),
('021-FG-AMC-8.75 RED STRAW'),
('021-FG-BIOSTRAW'),
('021-FG-RED MILKSHK STRAW 7.75"'),
('021-FG-RMHC_MCD'),
('021-FG-WENDY''S 9" STRAW - RED'),
('021-WRAPPED DQ STRAWS'),
('021-WRAPPEDJIBSTRAWS'),
('021-WRAPPEDJUMBOCSTRAW'),
('021-WRAPPEDJUMBOSTRAWS'),
('021-WRAPPEDRALLYSTRAW')


INSERT INTO validation.RangeItemList VALUES
('021-FG-MCDSTIRRER'),
('021-JIB COFFEE STIRRER')


INSERT INTO validation.AutoItemList VALUES
('021-GLOVES L 07606-021'),
('021-GLOVES M 07605-021'),
('021-GLOVES S 07604-018'),
('021-GLOVES XL 07607-012'),
('021-GLOVES XXL'),
('021-FG SOUP SPOON'),
('021-FG 2PC FORK/KNIFE KIT'),
('021-FG 9" SPOON WHITE')

GO
CREATE VIEW data.ViewValidationPalletCounts AS
SELECT lists.ItemNumber,
ISNULL(pc.RequiredCount,0) AS RequiredCount

FROM (
	SELECT ItemNumber FROM [validation].[PalletItemList]
	UNION
	SELECT ItemNumber FROM [validation].[RangeItemList]
	UNION
	SELECT ItemNumber FROM [validation].[AutoItemList]
) lists

LEFT OUTER JOIN [validation].[PalletCount] pc
ON pc.ItemNumber = lists.ItemNumber



GO
CREATE FUNCTION [dbo].[fn_SplitCharList]
(
      @ItemList varchar(MAX)
)
RETURNS 
@ParsedList TABLE
(
      Item VARCHAR(MAX)
)
AS
BEGIN
      DECLARE @Item VARCHAR(MAX), @Pos int

      SET @ItemList = LTRIM(RTRIM(@ItemList))+ ','
      SET @Pos = CHARINDEX(',', @ItemList, 1)

      IF REPLACE(@ItemList, ',', '') <> ''
      BEGIN
            WHILE @Pos > 0
            BEGIN
                  SET @Item = LTRIM(RTRIM(LEFT(@ItemList, @Pos - 1)))
                  IF @Item <> ''
                  BEGIN
                        INSERT INTO @ParsedList (Item) 
                        VALUES (@Item)
                  END
                  SET @ItemList = RIGHT(@ItemList, LEN(@ItemList) - @Pos)
                  SET @Pos = CHARINDEX(',', @ItemList, 1)
            END
      END   
      RETURN
END


GO
CREATE PROCEDURE [validation].[CheckExistingCaseBarcodes]
(
    @CasesString VARCHAR(MAX)
)
AS
BEGIN
	SELECT TOP 1 Pallet, CaseBarcode

	FROM [data].pallets p

	INNER JOIN [dbo].[fn_SplitCharList] (@CasesString) cs
	ON p.CaseBarcode = cs.Item
END


GO
CREATE PROCEDURE [data].[RangeInsert]
@ItemNumber VARCHAR(35),
@Pallet CHAR(20),
@Timestamp DATETIME2,
@UploadUsername VARCHAR(30),
@StartCase INT,
@EndCase INT,
@Shift CHAR(1)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CURRENT AS INT

    SET @CURRENT = @StartCase

    WHILE @CURRENT <= @EndCase
    BEGIN
        INSERT INTO data.pallets
        VALUES
        (@ItemNumber, 'Range' + CAST(@CURRENT AS VARCHAR(20)), @Pallet, @Shift, @Timestamp, @UploadUsername)
        SET @CURRENT += 1
    END

END


CREATE SEQUENCE data.SequenceAutoInsert
	AS INT
	START WITH 1
	INCREMENT BY 1

GO
CREATE PROCEDURE [data].[AutoInsert]
@ItemNumber VARCHAR(35),
@Pallet CHAR(20),
@Timestamp DATETIME2,
@UploadUsername VARCHAR(30),
@InsertQuantity INT,
@Shift CHAR(1)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @NexutAutoValue INT = NEXT VALUE FOR data.SequenceAutoInsert
	DECLARE @CURRENT INT = @NexutAutoValue
	DECLARE @EndCase INT = @Current + @InsertQuantity - 1


    SET @CURRENT = @NexutAutoValue

    WHILE @CURRENT <= @EndCase
    BEGIN
        INSERT INTO data.pallets
        VALUES
        (@ItemNumber, 'Auto' + CAST(@CURRENT AS VARCHAR(20)), @Pallet, @Shift, @Timestamp, @UploadUsername)
        SET @CURRENT += 1
    END

END






SELECT TOP 100 * 

FROM users.permissions





SELECT TOP 100 * 

FROM data.pallets