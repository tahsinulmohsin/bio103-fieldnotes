import { version } from "@/lib/version";

export function GET() {
  return Response.json({ status: "ok", app: "bio103-fieldnotes", version });
}
