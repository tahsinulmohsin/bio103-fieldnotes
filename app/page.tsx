import StudyApp from "@/components/study-app";
import courseFall2026 from "@/data/course-fall2026.json";
import courseFall2025 from "@/data/course.json";
import type { Course } from "@/lib/types";

export default function Home() {
  return (
    <StudyApp
      courseFall2026={courseFall2026 as unknown as Course}
      courseFall2025={courseFall2025 as unknown as Course}
    />
  );
}
