"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("personalix_token");
      if (token) {
        router.push("/dashboard");
      } else {
        router.push("/login");
      }
    }
  }, [router]);

  return null;
}
