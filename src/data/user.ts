import prisma from './prisma.js'

export async function getOrCreateUser(user: { id: string }) {
  return prisma.user.upsert({
    where: { id: user.id },
    update: {},
    create: { id: user.id },
  })
}
