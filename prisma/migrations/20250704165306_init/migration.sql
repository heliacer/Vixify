/*
  Warnings:

  - You are about to drop the column `coinEmojiId` on the `Guild` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Guild" DROP COLUMN "coinEmojiId",
ADD COLUMN     "coinEmoji" TEXT;
