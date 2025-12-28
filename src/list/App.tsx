/**
 * List Widget Template
 *
 * A vertical list with thumbnails - perfect for:
 * - Rankings and leaderboards
 * - Search results
 * - Task lists
 * - Article lists
 */

import React, { useState } from "react";
import { Star, PlusCircle, Check, ChevronRight } from "lucide-react";
import { Button } from "@openai/apps-sdk-ui/components/Button";
import { useWidgetProps } from "../use-widget-props";
import { useWidgetState } from "../use-widget-state";
import { useTheme } from "../use-theme";

type ListItem = {
  id: string;
  title: string;
  subtitle?: string;
  image?: string;
  rating?: number;
  meta?: string;
  badge?: string;
};

type ToolOutput = {
  title: string;
  subtitle?: string;
  headerImage?: string;
  items: ListItem[];
  actionLabel?: string;
};

type WidgetState = {
  selectedIds: string[];
};

const defaultProps: ToolOutput = {
  title: "Top Recommendations",
  subtitle: "Curated picks just for you",
  headerImage: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=200&h=200&fit=crop",
  actionLabel: "Save List",
  items: [
    {
      id: "1",
      title: "The Modern Kitchen",
      subtitle: "Contemporary American",
      image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=100&h=100&fit=crop",
      rating: 4.9,
      meta: "San Francisco",
      badge: "#1",
    },
    {
      id: "2",
      title: "Bella Italia",
      subtitle: "Authentic Italian",
      image: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=100&h=100&fit=crop",
      rating: 4.8,
      meta: "Oakland",
      badge: "#2",
    },
    {
      id: "3",
      title: "Sakura Japanese",
      subtitle: "Sushi & Izakaya",
      image: "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=100&h=100&fit=crop",
      rating: 4.7,
      meta: "Berkeley",
      badge: "#3",
    },
    {
      id: "4",
      title: "Taco Loco",
      subtitle: "Mexican Street Food",
      image: "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=100&h=100&fit=crop",
      rating: 4.6,
      meta: "San Jose",
    },
    {
      id: "5",
      title: "Golden Dragon",
      subtitle: "Cantonese Cuisine",
      image: "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=100&h=100&fit=crop",
      rating: 4.5,
      meta: "Palo Alto",
    },
  ],
};

export default function App() {
  const props = useWidgetProps<ToolOutput>(defaultProps);
  const theme = useTheme() ?? "light";
  const [widgetState, setWidgetState] = useWidgetState<WidgetState>({
    selectedIds: [],
  });

  const isDark = theme === "dark";

  const toggleItem = (id: string) => {
    setWidgetState((prev) => {
      const selectedIds = prev?.selectedIds ?? [];
      const isSelected = selectedIds.includes(id);
      return {
        ...prev,
        selectedIds: isSelected
          ? selectedIds.filter((i) => i !== id)
          : [...selectedIds, id],
      };
    });
  };

  const isSelected = (id: string) => widgetState?.selectedIds?.includes(id) ?? false;

  return (
    <div
      className={`w-full rounded-2xl border overflow-hidden ${
        isDark ? "bg-gray-900 border-gray-700" : "bg-white border-gray-200"
      }`}
    >
      {/* Header */}
      <div className={`flex items-center gap-4 p-4 border-b ${isDark ? "border-gray-700" : "border-gray-100"}`}>
        {props.headerImage && (
          <img
            src={props.headerImage}
            alt=""
            className="w-16 h-16 rounded-xl object-cover ring-1 ring-black/5"
          />
        )}
        <div className="flex-1 min-w-0">
          <h1 className={`text-lg font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>
            {props.title}
          </h1>
          {props.subtitle && (
            <p className={`text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>
              {props.subtitle}
            </p>
          )}
        </div>
        {props.actionLabel && (
          <Button variant="solid" color="primary" className="hidden sm:flex">
            {props.actionLabel}
          </Button>
        )}
      </div>

      {/* List Items */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {props.items.map((item, index) => (
          <div
            key={item.id}
            className={`flex items-center gap-3 px-4 py-3 transition-colors cursor-pointer ${
              isSelected(item.id)
                ? isDark
                  ? "bg-blue-900/20"
                  : "bg-blue-50"
                : isDark
                ? "hover:bg-gray-800"
                : "hover:bg-gray-50"
            }`}
            onClick={() => toggleItem(item.id)}
          >
            {/* Thumbnail */}
            {item.image && (
              <div className="relative flex-shrink-0">
                <img
                  src={item.image}
                  alt={item.title}
                  className="w-11 h-11 rounded-lg object-cover ring-1 ring-black/5"
                />
                {item.badge && (
                  <span className="absolute -top-1 -left-1 w-5 h-5 flex items-center justify-center text-[10px] font-bold bg-orange-500 text-white rounded-full">
                    {item.badge}
                  </span>
                )}
              </div>
            )}

            {/* Rank number (if no image) */}
            {!item.image && (
              <div className={`w-8 text-center text-sm ${isDark ? "text-gray-500" : "text-gray-400"}`}>
                {index + 1}
              </div>
            )}

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h3 className={`font-medium truncate ${isDark ? "text-white" : "text-gray-900"}`}>
                  {item.title}
                </h3>
              </div>
              <div className="flex items-center gap-3 mt-0.5">
                {item.rating && (
                  <div className={`flex items-center gap-1 text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                    <Star className="w-3 h-3 fill-current text-yellow-500" />
                    <span>{item.rating.toFixed(1)}</span>
                  </div>
                )}
                {item.subtitle && (
                  <span className={`text-sm ${isDark ? "text-gray-500" : "text-gray-400"}`}>
                    {item.subtitle}
                  </span>
                )}
              </div>
            </div>

            {/* Meta & Action */}
            <div className="flex items-center gap-2 flex-shrink-0">
              {item.meta && (
                <span className={`hidden sm:block text-sm ${isDark ? "text-gray-500" : "text-gray-400"}`}>
                  {item.meta}
                </span>
              )}
              {isSelected(item.id) ? (
                <Check className="w-5 h-5 text-blue-500" />
              ) : (
                <PlusCircle className={`w-5 h-5 ${isDark ? "text-gray-500" : "text-gray-400"}`} />
              )}
            </div>
          </div>
        ))}

        {props.items.length === 0 && (
          <div className={`py-8 text-center ${isDark ? "text-gray-500" : "text-gray-400"}`}>
            No items found.
          </div>
        )}
      </div>

      {/* Mobile Action */}
      {props.actionLabel && (
        <div className="sm:hidden p-4 border-t border-gray-100 dark:border-gray-800">
          <Button variant="solid" color="primary" className="w-full">
            {props.actionLabel}
          </Button>
        </div>
      )}

      {/* Footer with selection count */}
      {(widgetState?.selectedIds?.length ?? 0) > 0 && (
        <div className={`px-4 py-3 border-t text-sm ${isDark ? "border-gray-700 text-gray-400" : "border-gray-100 text-gray-500"}`}>
          {widgetState?.selectedIds?.length} item{widgetState?.selectedIds?.length !== 1 ? "s" : ""} selected
        </div>
      )}
    </div>
  );
}
