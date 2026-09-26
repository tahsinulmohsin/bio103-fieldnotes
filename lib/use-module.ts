"use client";

import { useEffect, useState } from "react";
import type { Module, Semester } from "@/lib/types";

const cache = new Map<string, Promise<Module>>();

function load(semester: Semester, id: string): Promise<Module> {
  const url = `/course-data/${semester}/${encodeURIComponent(id)}`;
  let pending = cache.get(url);
  if (!pending) {
    pending = fetch(url).then((res) => {
      if (!res.ok) throw new Error(`Could not load this topic (${res.status})`);
      return res.json() as Promise<Module>;
    });
    pending.catch(() => cache.delete(url));
    cache.set(url, pending);
  }
  return pending;
}

/** A topic's full content, fetched once per visit and then reused. */
export function useModule(semester: Semester, id: string) {
  const [state, setState] = useState<{ key: string; module?: Module; error?: string }>({ key: "" });
  const [attempt, setAttempt] = useState(0);
  const key = `${semester}/${id}`;
  useEffect(() => {
    let live = true;
    load(semester, id).then(
      (module) => live && setState({ key, module }),
      (e: Error) => live && setState({ key, error: e.message }),
    );
    return () => {
      live = false;
    };
  }, [semester, id, key, attempt]);
  const current = state.key === key ? state : { key };
  return {
    module: current.module,
    error: current.error,
    retry: () => {
      setState({ key: "" });
      setAttempt((n) => n + 1);
    },
  };
}
