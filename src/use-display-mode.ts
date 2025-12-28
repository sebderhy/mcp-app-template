import { useOpenAiGlobal } from "./use-openai-global";
import { type DisplayMode } from "./types";

/**
 * React hook to get the current display mode.
 * - "inline": Default card view in the chat
 * - "fullscreen": Full screen view with composer overlay
 * - "pip": Picture-in-picture floating window
 *
 * @example
 * const displayMode = useDisplayMode();
 * if (displayMode === "fullscreen") {
 *   // Show expanded UI
 * }
 */
export const useDisplayMode = (): DisplayMode | null => {
  return useOpenAiGlobal("displayMode");
};
