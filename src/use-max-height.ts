import { useOpenAiGlobal } from "./use-openai-global";

/**
 * React hook to get the maximum height constraint from the ChatGPT host.
 * Use this to prevent your widget from overflowing.
 *
 * @example
 * const maxHeight = useMaxHeight();
 * return <div style={{ maxHeight: maxHeight ?? undefined }}>...</div>;
 */
export const useMaxHeight = (): number | null => {
  return useOpenAiGlobal("maxHeight");
};
