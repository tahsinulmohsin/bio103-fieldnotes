import { courses, moduleForClient } from "@/lib/courses";
import type { Semester } from "@/lib/types";

// Every topic is prerendered to a static JSON file at build time.
export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  return (Object.keys(courses) as Semester[]).flatMap((semester) =>
    courses[semester].modules.map((m) => ({ semester, module: m.id })),
  );
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ semester: string; module: string }> },
) {
  const { semester, module } = await params;
  const found =
    semester in courses ? moduleForClient(semester as Semester, module) : null;
  if (!found) return Response.json({ error: "Unknown topic" }, { status: 404 });
  return Response.json(found);
}
