-- CreateTable
CREATE TABLE "ItemTemplate" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "emoji" TEXT,
    "description" TEXT,
    "isStackable" BOOLEAN NOT NULL DEFAULT true,
    "defaultDurability" INTEGER,

    CONSTRAINT "ItemTemplate_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "UserItem" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "templateId" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL DEFAULT 1,
    "durability" INTEGER,
    "metadata" JSONB,

    CONSTRAINT "UserItem_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "ItemTemplate_name_key" ON "ItemTemplate"("name");

-- CreateIndex
CREATE UNIQUE INDEX "UserItem_userId_templateId_key" ON "UserItem"("userId", "templateId");

-- AddForeignKey
ALTER TABLE "UserItem" ADD CONSTRAINT "UserItem_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserItem" ADD CONSTRAINT "UserItem_templateId_fkey" FOREIGN KEY ("templateId") REFERENCES "ItemTemplate"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
