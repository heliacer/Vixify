/*
  Warnings:

  - You are about to drop the column `coins` on the `User` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "GuildUser" ADD COLUMN     "coins" INTEGER NOT NULL DEFAULT 0;

-- AlterTable
ALTER TABLE "User" DROP COLUMN "coins";
