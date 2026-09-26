import StudyApp from "@/components/study-app";
import { courseIndex, courses } from "@/lib/courses";
import { version } from "@/lib/version";

export default function Home() {
  // Only the index (titles, counts, slide lists) ships with the page;
  // each topic's notes, cards and questions load when it is opened.
  return (
    <StudyApp
      courses={{
        fall2026: courseIndex(courses.fall2026),
        fall2025: courseIndex(courses.fall2025),
      }}
      version={version}
    />
  );
}
