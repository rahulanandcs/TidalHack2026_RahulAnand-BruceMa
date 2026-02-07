import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, Snowflake, Briefcase, Building2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function CareerFairAI() {
  const [resumeUploaded, setResumeUploaded] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-100 to-blue-200 text-slate-800 p-8">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-bold text-center mb-4 flex justify-center items-center gap-2"
      >
        <Snowflake className="w-8 h-8" /> CareerFair AI
      </motion.h1>

      <p className="text-center max-w-2xl mx-auto mb-10 text-slate-600">
        Upload your resume and instantly get matched with companies hiring candidates like you — plus tailored talking points for every booth.
      </p>

      {/* Resume Upload */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-xl mx-auto">
        <Card className="rounded-2xl shadow-lg">
          <CardContent className="p-6 text-center">
            <Upload className="mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Upload Your Resume</h2>
            <p className="text-sm text-slate-500 mb-4">
              We scan your experience using NLP to extract skills, projects, and interests.
            </p>
            <Button onClick={() => setResumeUploaded(true)} className="rounded-xl">
              Upload Resume
            </Button>
          </CardContent>
        </Card>
      </motion.div>

      {/* Results */}
      {resumeUploaded && (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto"
        >
          {/* Company Matches */}
          <Card className="rounded-2xl shadow-md">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Building2 /> Best Company Matches
              </h3>
              <ul className="space-y-3">
                <li className="bg-white/60 p-3 rounded-xl">
                  <strong>Snowflake Inc.</strong>
                  <p className="text-sm">Looking for: Data Science Interns, Python, SQL</p>
                </li>
                <li className="bg-white/60 p-3 rounded-xl">
                  <strong>Microsoft</strong>
                  <p className="text-sm">Looking for: Software Engineering Interns, React, Cloud</p>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Talking Points */}
          <Card className="rounded-2xl shadow-md">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Briefcase /> AI-Generated Talking Points
              </h3>
              <ul className="space-y-3 text-sm">
                <li className="bg-white/60 p-3 rounded-xl">
                  Mention your Python data analysis project and ask about Snowflake's data pipeline team.
                </li>
                <li className="bg-white/60 p-3 rounded-xl">
                  Highlight your React experience and interest in scalable frontend systems at Microsoft.
                </li>
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Footer Pitch */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-16 text-center">
        <p className="text-slate-600 max-w-3xl mx-auto">
          CareerFair AI bridges students and employers using machine learning — reducing awkward conversations, improving hiring efficiency, and helping students make meaningful first impressions.
        </p>
      </motion.div>
    </div>
  );
}
