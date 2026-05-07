"use client";

import { use } from "react";
import Link from "next/link";
import { EditProblemForm } from "../../_components/inline-editors";

export default function EditProblemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-6">
          <Link
            href="/admin"
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            ← Admin
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Edit Problem</h1>
        </div>

        <EditProblemForm
          problemId={id}
          onClose={() => {
            // In a standalone tab, just close the window after save
            window.close();
          }}
        />
      </div>
    </div>
  );
}
