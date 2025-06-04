import { createFileRoute } from "@tanstack/react-router";
import JobPostingGenerator from "@/components/JobPostings/JobPostingGenerator";

export const Route = createFileRoute("/_layout/job-postings")({
  component: JobPostingGenerator,
});