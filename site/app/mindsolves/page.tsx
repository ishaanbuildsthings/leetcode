import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import * as problemService from "@/lib/services/problem.service";
import { transformProblemWithRelations } from "@/lib/transforms";
import { ProblemsList } from "@/components/ProblemsList";
import { AuthProvider } from "@/contexts/AuthContext";

export default async function MindsolvesPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  let userId: string | null = null;
  let isAdmin = false;
  
  if (user) {
    userId = user.id;
    const dbUser = await prisma.users.findUnique({ where: { id: user.id } });
    isAdmin = dbUser?.is_admin ?? false;
  }
  
  const problemsData = await problemService.unsafe_listProblems();
  const mindsolves = problemsData
    .map(transformProblemWithRelations)
    .filter(problem => problem.drillType === "mindsolve");

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <ProblemsList
        problems={mindsolves}
        title="Mindsolves"
        description="Problems to mindsolve and think through"
        activePath="/mindsolves"
      />
    </AuthProvider>
  );
}

