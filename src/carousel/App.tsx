/**
 * Carousel Widget Template
 *
 * A horizontal scrolling carousel of cards - perfect for:
 * - Product showcases
 * - Restaurant/place listings
 * - Image galleries
 * - Recommendation lists
 */

import React, { useState, useRef, useEffect } from "react";
import { ArrowLeft, ArrowRight, Star, MapPin } from "lucide-react";
import { useWidgetProps } from "../use-widget-props";
import { useTheme } from "../use-theme";

type CarouselItem = {
  id: string;
  title: string;
  subtitle?: string;
  image: string;
  rating?: number;
  location?: string;
  price?: string;
  badge?: string;
};

type ToolOutput = {
  title?: string;
  items: CarouselItem[];
};

const defaultProps: ToolOutput = {
  title: "Recommended Places",
  items: [
    {
      id: "1",
      title: "Golden Gate Bistro",
      subtitle: "Modern American cuisine",
      image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop",
      rating: 4.8,
      location: "San Francisco",
      price: "$$$",
      badge: "Popular",
    },
    {
      id: "2",
      title: "Marina Bay Kitchen",
      subtitle: "Fresh seafood & coastal flavors",
      image: "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
      rating: 4.6,
      location: "Oakland",
      price: "$$",
    },
    {
      id: "3",
      title: "Sunset Terrace",
      subtitle: "Rooftop dining experience",
      image: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop",
      rating: 4.9,
      location: "Berkeley",
      price: "$$$$",
      badge: "New",
    },
    {
      id: "4",
      title: "The Local Table",
      subtitle: "Farm-to-table favorites",
      image: "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=400&h=300&fit=crop",
      rating: 4.5,
      location: "Palo Alto",
      price: "$$",
    },
    {
      id: "5",
      title: "Urban Spice",
      subtitle: "Contemporary Indian fusion",
      image: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=300&fit=crop",
      rating: 4.7,
      location: "San Jose",
      price: "$$",
    },
  ],
};

export default function App() {
  const props = useWidgetProps<ToolOutput>(defaultProps);
  const theme = useTheme() ?? "light";
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const updateScrollButtons = () => {
    if (!scrollRef.current) return;
    const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
    setCanScrollLeft(scrollLeft > 0);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
  };

  useEffect(() => {
    updateScrollButtons();
    const ref = scrollRef.current;
    if (ref) {
      ref.addEventListener("scroll", updateScrollButtons);
      return () => ref.removeEventListener("scroll", updateScrollButtons);
    }
  }, []);

  const scroll = (direction: "left" | "right") => {
    if (!scrollRef.current) return;
    const scrollAmount = 300;
    scrollRef.current.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  };

  const isDark = theme === "dark";

  return (
    <div className={`relative w-full py-4 ${isDark ? "bg-gray-900" : "bg-white"}`}>
      {/* Header */}
      {props.title && (
        <h2 className={`px-4 mb-4 text-lg font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>
          {props.title}
        </h2>
      )}

      {/* Carousel Container */}
      <div className="relative">
        {/* Scroll Container */}
        <div
          ref={scrollRef}
          className="flex gap-4 overflow-x-auto px-4 pb-2 scrollbar-hide"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          {props.items.map((item) => (
            <article
              key={item.id}
              className={`flex-shrink-0 w-64 rounded-2xl overflow-hidden border transition-shadow hover:shadow-lg cursor-pointer ${
                isDark
                  ? "bg-gray-800 border-gray-700"
                  : "bg-white border-gray-200"
              }`}
            >
              {/* Image */}
              <div className="relative h-40 overflow-hidden">
                <img
                  src={item.image}
                  alt={item.title}
                  className="w-full h-full object-cover"
                />
                {item.badge && (
                  <span className="absolute top-2 left-2 px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded-full">
                    {item.badge}
                  </span>
                )}
              </div>

              {/* Content */}
              <div className="p-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className={`font-semibold truncate ${isDark ? "text-white" : "text-gray-900"}`}>
                    {item.title}
                  </h3>
                  {item.rating && (
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className={`text-sm ${isDark ? "text-gray-300" : "text-gray-600"}`}>
                        {item.rating}
                      </span>
                    </div>
                  )}
                </div>

                {item.subtitle && (
                  <p className={`text-sm mt-1 truncate ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                    {item.subtitle}
                  </p>
                )}

                <div className="flex items-center justify-between mt-2">
                  {item.location && (
                    <div className={`flex items-center gap-1 text-xs ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                      <MapPin className="w-3 h-3" />
                      <span>{item.location}</span>
                    </div>
                  )}
                  {item.price && (
                    <span className={`text-sm font-medium ${isDark ? "text-green-400" : "text-green-600"}`}>
                      {item.price}
                    </span>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>

        {/* Navigation Arrows */}
        {canScrollLeft && (
          <button
            onClick={() => scroll("left")}
            className={`absolute left-2 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full flex items-center justify-center shadow-lg transition-colors ${
              isDark
                ? "bg-gray-700 hover:bg-gray-600 text-white"
                : "bg-white hover:bg-gray-100 text-gray-900"
            }`}
            aria-label="Scroll left"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
        )}
        {canScrollRight && (
          <button
            onClick={() => scroll("right")}
            className={`absolute right-2 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full flex items-center justify-center shadow-lg transition-colors ${
              isDark
                ? "bg-gray-700 hover:bg-gray-600 text-white"
                : "bg-white hover:bg-gray-100 text-gray-900"
            }`}
            aria-label="Scroll right"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        )}

        {/* Edge Gradients */}
        {canScrollLeft && (
          <div
            className={`absolute left-0 top-0 bottom-0 w-8 pointer-events-none ${
              isDark
                ? "bg-gradient-to-r from-gray-900 to-transparent"
                : "bg-gradient-to-r from-white to-transparent"
            }`}
          />
        )}
        {canScrollRight && (
          <div
            className={`absolute right-0 top-0 bottom-0 w-8 pointer-events-none ${
              isDark
                ? "bg-gradient-to-l from-gray-900 to-transparent"
                : "bg-gradient-to-l from-white to-transparent"
            }`}
          />
        )}
      </div>
    </div>
  );
}
