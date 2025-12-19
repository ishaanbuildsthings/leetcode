import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { appRouter } from "@/server/routers/_app";
import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import type { Context } from "@/server/trpc";

async function createContext(): Promise<Context> {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { userId: null, isAdmin: false };
  }
  
  const dbUser = await prisma.users.findUnique({
    where: { id: user.id },
  });
  
  return {
    userId: user.id,
    isAdmin: dbUser?.is_admin ?? false,
  };
}

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req,
    router: appRouter,
    createContext,
  });

export { handler as GET, handler as POST };

