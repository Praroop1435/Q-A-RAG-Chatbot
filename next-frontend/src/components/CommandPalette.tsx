"use client";

import { useEffect, useState } from "react";
import { Command } from "cmdk";
import { FileUp, MessageSquare, Moon, Sun, Trash } from "lucide-react";

export function CommandPalette({
  open,
  setOpen,
  onClear,
}: {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  onClear: () => void;
}) {
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [setOpen]);

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Global Command Menu"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm transition-all"
    >
      <div className="w-full max-w-lg overflow-hidden rounded-xl border border-neutral-800 bg-[#0a0a0a] shadow-2xl">
        <Command.Input
          placeholder="Type a command or search..."
          className="w-full border-b border-neutral-800 bg-transparent px-4 py-3 text-sm text-neutral-50 placeholder-neutral-500 focus:outline-none focus:ring-0"
        />
        <Command.List className="max-h-80 overflow-y-auto p-2">
          <Command.Empty className="py-6 text-center text-sm text-neutral-500">
            No results found.
          </Command.Empty>

          <Command.Group heading="Actions" className="px-2 text-xs font-medium text-neutral-500 pb-2">
            <Command.Item
              onSelect={() => {
                setOpen(false);
                document.getElementById("pdf-upload")?.click();
              }}
              className="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm text-neutral-300 aria-selected:bg-neutral-800 aria-selected:text-neutral-50"
            >
              <FileUp className="h-4 w-4" />
              Upload PDF
            </Command.Item>
            <Command.Item
              onSelect={() => {
                setOpen(false);
                onClear();
              }}
              className="flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm text-neutral-300 aria-selected:bg-neutral-800 aria-selected:text-neutral-50"
            >
              <Trash className="h-4 w-4" />
              Clear Chat
            </Command.Item>
          </Command.Group>
        </Command.List>
      </div>
    </Command.Dialog>
  );
}
