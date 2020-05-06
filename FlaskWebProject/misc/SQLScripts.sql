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

CREATE TABLE [validation].[StirrerItemList](
	[StirrerItemListID] INT PRIMARY KEY IDENTITY(1,1),
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


CREATE PROCEDURE [users].[UpdatePermissionsForUser]

AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

	MERGE [users].[PermissionsAssignment] AS target
	USING (

		SELECT UserID,
		PermissionID
		
		FROM [users].[PermissionsAssignmentStaging]

		) AS source 
	ON (target.UserID = source.UserID
		AND target.PermissionID = source.PermissionID)
	WHEN NOT MATCHED BY TARGET THEN
		INSERT 
		VALUES (
			source.UserID,
			source.PermissionID
		)
	WHEN NOT MATCHED BY SOURCE THEN
		DELETE;

	TRUNCATE TABLE [users].[PermissionsAssignmentStaging]

END



CREATE PROCEDURE [users].[UpdateDefaultPermissions]

AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON


	MERGE [Users].PermissionsDefaults AS target
	USING (

		SELECT PermissionID 
		
		FROM users.PermissionsAssignmentStaging

		) AS source 
	ON (target.PermissionID = source.PermissionID)
	WHEN NOT MATCHED BY TARGET THEN
		INSERT 
		VALUES (
			source.PermissionID
		)
	WHEN NOT MATCHED BY SOURCE THEN
		DELETE;

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


INSERT INTO users.Permissions VALUES
('/user/create'),
('/user/delete'),
('/user/permissions'),
('/pallets/upload'),
('/pallets/stirrer'),
('/pallets/delete'),
('/salesorder/upload'),
('/salesorder/delete'),
('/validation/palletitem'),
('/validation/stirreritem'),
('/validation/palletcount')



INSERT INTO validation.PalletItemList VALUES
('021-FG 10.25 BLUE SPOON STRAW'),
('021-FG 2PC FORK/KNIFE KIT'),
('021-FG 9" SPOON WHITE'),
('021-FG BIOSTRAW 7200 GREEN'),
('021-FG SOUP SPOON'),
('021-FG TEAL AMERCARE STRAW'),
('021-FG-10.25 SHEETZ RED'),
('021-FG-7.75 WHITE W/RED STRAW'),
('021-FG-8.75" PURPLE WRAP STRAW'),
('021-FG-AMC-8.75 RED STRAW'),
('021-FG-BIOSTRAW'),
('021-FG-RED MILKSHK STRAW 7.75"'),
('021-FG-RMHC_MCD'),
('021-FG-WENDY''S 9" STRAW - RED'),
('021-GLOVES L 07606-021'),
('021-GLOVES M 07605-021'),
('021-GLOVES S 07604-018'),
('021-GLOVES XL 07607-012'),
('021-GLOVES XXL'),
('021-WRAPPED DQ STRAWS'),
('021-WRAPPEDJIBSTRAWS'),
('021-WRAPPEDJUMBOCSTRAW'),
('021-WRAPPEDJUMBOSTRAWS'),
('021-WRAPPEDRALLYSTRAW')


INSERT INTO validation.StirrerItemList VALUES
('021-FG-MCDSTIRRER'),
('021-JIB COFFEE STIRRER')

GO
CREATE VIEW data.ViewValidationPalletCounts AS
SELECT lists.ItemNumber,
ISNULL(pc.RequiredCount,0) AS RequiredCount

FROM (
	SELECT ItemNumber FROM [validation].[PalletItemList]
	UNION
	SELECT ItemNumber FROM [validation].[StirrerItemList]
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
CREATE PROCEDURE [data].[FirstLastInsert]
@ItemNumber VARCHAR(35),
@Pallet CHAR(20),
@Timestamp DATETIME2,
@UploadUsername VARCHAR(30),
@StartCase INT,
@EndCase INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CURRENT AS INT

    SET @CURRENT = @StartCase

    WHILE @CURRENT <= @EndCase
    BEGIN
        INSERT INTO data.pallets
        VALUES
        (@ItemNumber, 'Stir' + CAST(@CURRENT AS VARCHAR(20)), @Pallet, @Timestamp, @UploadUsername)
        SET @CURRENT += 1
    END

END




SELECT TOP 100 * 

FROM users.permissions



SELECT TOP 100 * 

FROM users.PermissionsAssignment


