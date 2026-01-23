/**
 * Travel Map Widget
 *
 * An interactive map widget for travel/tourism apps - perfect for:
 * - TripAdvisor-style destination exploration
 * - Hotel, restaurant, and attraction locations
 * - Travel itinerary visualization
 * - Points of interest with ratings and details
 */

import React, { useState, useRef, useEffect } from "react";
import {
  MapPin,
  Star,
  Navigation,
  Utensils,
  Hotel,
  Camera,
  Coffee,
  ShoppingBag,
  X,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { useWidgetProps } from "../use-widget-props";
import { useWidgetState } from "../use-widget-state";
import { useTheme } from "../use-theme";

type PlaceCategory = "restaurant" | "hotel" | "attraction" | "cafe" | "shop";

type Place = {
  id: string;
  name: string;
  category: PlaceCategory;
  description?: string;
  image?: string;
  rating?: number;
  reviewCount?: number;
  priceLevel?: string;
  address?: string;
  lat: number;
  lng: number;
  tags?: string[];
};

type MapBounds = {
  north: number;
  south: number;
  east: number;
  west: number;
};

type ToolOutput = {
  title?: string;
  subtitle?: string;
  places: Place[];
  center?: { lat: number; lng: number };
  zoom?: number;
};

type WidgetState = {
  selectedPlaceId: string | null;
  zoom: number;
  center: { lat: number; lng: number };
};

const defaultProps: ToolOutput = {
  title: "Explore San Francisco",
  subtitle: "Top-rated places near you",
  places: [
    {
      id: "1",
      name: "Golden Gate Bistro",
      category: "restaurant",
      description: "Award-winning modern American cuisine with stunning bay views",
      image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop",
      rating: 4.8,
      reviewCount: 2847,
      priceLevel: "$$$",
      address: "123 Marina Blvd, San Francisco",
      lat: 37.8024,
      lng: -122.4058,
      tags: ["Fine Dining", "Waterfront"],
    },
    {
      id: "2",
      name: "The Fairmont",
      category: "hotel",
      description: "Historic luxury hotel atop Nob Hill with panoramic city views",
      image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop",
      rating: 4.7,
      reviewCount: 5234,
      priceLevel: "$$$$",
      address: "950 Mason St, San Francisco",
      lat: 37.7922,
      lng: -122.4100,
      tags: ["Luxury", "Historic"],
    },
    {
      id: "3",
      name: "Alcatraz Island",
      category: "attraction",
      description: "Iconic former federal prison with guided tours and bay views",
      image: "https://images.unsplash.com/photo-1534050359320-02900022671e?w=400&h=300&fit=crop",
      rating: 4.9,
      reviewCount: 18432,
      address: "Alcatraz Island, San Francisco Bay",
      lat: 37.8267,
      lng: -122.4230,
      tags: ["Historic", "Must See"],
    },
    {
      id: "4",
      name: "Blue Bottle Coffee",
      category: "cafe",
      description: "Artisan coffee roasters known for pour-over and espresso",
      image: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=300&fit=crop",
      rating: 4.5,
      reviewCount: 1256,
      priceLevel: "$$",
      address: "66 Mint St, San Francisco",
      lat: 37.7825,
      lng: -122.4024,
      tags: ["Local Favorite"],
    },
    {
      id: "5",
      name: "Ferry Building Marketplace",
      category: "shop",
      description: "Historic waterfront marketplace with local artisan vendors",
      image: "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=400&h=300&fit=crop",
      rating: 4.6,
      reviewCount: 8921,
      address: "1 Ferry Building, San Francisco",
      lat: 37.7956,
      lng: -122.3935,
      tags: ["Shopping", "Food Hall"],
    },
    {
      id: "6",
      name: "Fisherman's Wharf",
      category: "attraction",
      description: "Bustling waterfront neighborhood with seafood and sea lions",
      image: "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=400&h=300&fit=crop",
      rating: 4.4,
      reviewCount: 12543,
      address: "Jefferson St, San Francisco",
      lat: 37.8080,
      lng: -122.4177,
      tags: ["Family Friendly", "Iconic"],
    },
  ],
  center: { lat: 37.7949, lng: -122.4094 },
  zoom: 13,
};

const categoryIcons: Record<PlaceCategory, React.ElementType> = {
  restaurant: Utensils,
  hotel: Hotel,
  attraction: Camera,
  cafe: Coffee,
  shop: ShoppingBag,
};

const categoryColors: Record<PlaceCategory, string> = {
  restaurant: "#ef4444",
  hotel: "#8b5cf6",
  attraction: "#f59e0b",
  cafe: "#6366f1",
  shop: "#10b981",
};

export default function App() {
  const props = useWidgetProps<ToolOutput>(defaultProps);
  const theme = useTheme() ?? "light";
  const [widgetState, setWidgetState] = useWidgetState<WidgetState>({
    selectedPlaceId: null,
    zoom: props.zoom ?? 13,
    center: props.center ?? { lat: 37.7949, lng: -122.4094 },
  });
  const mapRef = useRef<HTMLDivElement>(null);

  const isDark = theme === "dark";
  const selectedPlace = props.places.find((p) => p.id === widgetState?.selectedPlaceId);

  // Calculate map bounds from places
  const bounds: MapBounds = React.useMemo(() => {
    if (props.places.length === 0) {
      return { north: 37.85, south: 37.75, east: -122.35, west: -122.5 };
    }
    const lats = props.places.map((p) => p.lat);
    const lngs = props.places.map((p) => p.lng);
    const padding = 0.02;
    return {
      north: Math.max(...lats) + padding,
      south: Math.min(...lats) - padding,
      east: Math.max(...lngs) + padding,
      west: Math.min(...lngs) - padding,
    };
  }, [props.places]);

  // Convert lat/lng to pixel position within the map container
  const latLngToPixel = (lat: number, lng: number) => {
    const x = ((lng - bounds.west) / (bounds.east - bounds.west)) * 100;
    const y = ((bounds.north - lat) / (bounds.north - bounds.south)) * 100;
    return { x: Math.max(5, Math.min(95, x)), y: Math.max(5, Math.min(95, y)) };
  };

  const selectPlace = (id: string | null) => {
    setWidgetState((prev) => ({ ...prev, selectedPlaceId: id }));
  };

  const navigatePlace = (direction: "prev" | "next") => {
    const currentIndex = props.places.findIndex((p) => p.id === widgetState?.selectedPlaceId);
    let newIndex: number;
    if (direction === "next") {
      newIndex = currentIndex < props.places.length - 1 ? currentIndex + 1 : 0;
    } else {
      newIndex = currentIndex > 0 ? currentIndex - 1 : props.places.length - 1;
    }
    selectPlace(props.places[newIndex].id);
  };

  const CategoryIcon = ({ category }: { category: PlaceCategory }) => {
    const Icon = categoryIcons[category] || MapPin;
    return <Icon className="w-4 h-4" />;
  };

  return (
    <div
      className={`relative w-full rounded-2xl overflow-hidden border ${
        isDark ? "bg-gray-900 border-gray-700" : "bg-white border-gray-200"
      }`}
    >
      {/* Header */}
      <div className={`px-4 py-3 border-b ${isDark ? "border-gray-700" : "border-gray-100"}`}>
        <div className="flex items-center justify-between">
          <div>
            {props.title && (
              <h2 className={`text-lg font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>
                {props.title}
              </h2>
            )}
            {props.subtitle && (
              <p className={`text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                {props.subtitle}
              </p>
            )}
          </div>
          <div className={`flex items-center gap-1 text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>
            <MapPin className="w-4 h-4" />
            <span>{props.places.length} places</span>
          </div>
        </div>

        {/* Category Legend */}
        <div className="flex flex-wrap gap-3 mt-3">
          {(Object.keys(categoryIcons) as PlaceCategory[]).map((cat) => {
            const count = props.places.filter((p) => p.category === cat).length;
            if (count === 0) return null;
            return (
              <div
                key={cat}
                className={`flex items-center gap-1.5 text-xs ${isDark ? "text-gray-400" : "text-gray-500"}`}
              >
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: categoryColors[cat] }}
                />
                <span className="capitalize">
                  {cat}s ({count})
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Map Container */}
      <div className="relative">
        <div
          ref={mapRef}
          className={`relative w-full h-72 ${
            isDark ? "bg-gray-800" : "bg-blue-50"
          }`}
          style={{
            backgroundImage: isDark
              ? `
                linear-gradient(rgba(55, 65, 81, 0.5) 1px, transparent 1px),
                linear-gradient(90deg, rgba(55, 65, 81, 0.5) 1px, transparent 1px)
              `
              : `
                linear-gradient(rgba(147, 197, 253, 0.3) 1px, transparent 1px),
                linear-gradient(90deg, rgba(147, 197, 253, 0.3) 1px, transparent 1px)
              `,
            backgroundSize: "40px 40px",
          }}
        >
          {/* Map Markers */}
          {props.places.map((place) => {
            const pos = latLngToPixel(place.lat, place.lng);
            const isSelected = widgetState?.selectedPlaceId === place.id;
            const color = categoryColors[place.category];

            return (
              <button
                key={place.id}
                onClick={() => selectPlace(isSelected ? null : place.id)}
                className={`absolute transform -translate-x-1/2 -translate-y-full transition-all duration-200 ${
                  isSelected ? "z-20 scale-125" : "z-10 hover:scale-110"
                }`}
                style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
              >
                <div
                  className={`relative flex items-center justify-center w-8 h-10 rounded-full shadow-lg ${
                    isSelected ? "ring-2 ring-white" : ""
                  }`}
                  style={{ backgroundColor: color }}
                >
                  <div className="text-white">
                    <CategoryIcon category={place.category} />
                  </div>
                  {/* Pin point */}
                  <div
                    className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-0 h-0"
                    style={{
                      borderLeft: "6px solid transparent",
                      borderRight: "6px solid transparent",
                      borderTop: `8px solid ${color}`,
                    }}
                  />
                </div>
                {/* Rating badge */}
                {place.rating && (
                  <div
                    className={`absolute -top-1 -right-1 px-1.5 py-0.5 text-[10px] font-bold rounded-full shadow ${
                      isDark ? "bg-gray-700 text-white" : "bg-white text-gray-900"
                    }`}
                  >
                    {place.rating}
                  </div>
                )}
              </button>
            );
          })}

          {/* Map Attribution */}
          <div
            className={`absolute bottom-2 right-2 text-[10px] px-2 py-1 rounded ${
              isDark ? "bg-gray-900/80 text-gray-400" : "bg-white/80 text-gray-500"
            }`}
          >
            Interactive Map View
          </div>
        </div>

        {/* Selected Place Card Overlay */}
        {selectedPlace && (
          <div className="absolute bottom-4 left-4 right-4 z-30">
            <article
              className={`rounded-xl overflow-hidden shadow-xl border ${
                isDark ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200"
              }`}
            >
              <div className="flex">
                {/* Image */}
                {selectedPlace.image && (
                  <div className="w-28 h-28 flex-shrink-0">
                    <img
                      src={selectedPlace.image}
                      alt={selectedPlace.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                {/* Content */}
                <div className="flex-1 p-3 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-2 h-2 rounded-full flex-shrink-0"
                          style={{ backgroundColor: categoryColors[selectedPlace.category] }}
                        />
                        <h3
                          className={`font-semibold truncate ${isDark ? "text-white" : "text-gray-900"}`}
                        >
                          {selectedPlace.name}
                        </h3>
                      </div>
                      {selectedPlace.description && (
                        <p
                          className={`text-xs mt-1 line-clamp-2 ${
                            isDark ? "text-gray-400" : "text-gray-500"
                          }`}
                        >
                          {selectedPlace.description}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => selectPlace(null)}
                      className={`p-1 rounded-full flex-shrink-0 ${
                        isDark ? "hover:bg-gray-700" : "hover:bg-gray-100"
                      }`}
                    >
                      <X className={`w-4 h-4 ${isDark ? "text-gray-400" : "text-gray-500"}`} />
                    </button>
                  </div>

                  <div className="flex items-center gap-3 mt-2">
                    {selectedPlace.rating && (
                      <div className="flex items-center gap-1">
                        <Star className="w-3.5 h-3.5 fill-yellow-400 text-yellow-400" />
                        <span className={`text-sm font-medium ${isDark ? "text-white" : "text-gray-900"}`}>
                          {selectedPlace.rating}
                        </span>
                        {selectedPlace.reviewCount && (
                          <span className={`text-xs ${isDark ? "text-gray-500" : "text-gray-400"}`}>
                            ({selectedPlace.reviewCount.toLocaleString()})
                          </span>
                        )}
                      </div>
                    )}
                    {selectedPlace.priceLevel && (
                      <span className={`text-sm ${isDark ? "text-green-400" : "text-green-600"}`}>
                        {selectedPlace.priceLevel}
                      </span>
                    )}
                  </div>

                  {/* Tags */}
                  {selectedPlace.tags && selectedPlace.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {selectedPlace.tags.map((tag) => (
                        <span
                          key={tag}
                          className={`text-[10px] px-2 py-0.5 rounded-full ${
                            isDark ? "bg-gray-700 text-gray-300" : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Navigation */}
              <div
                className={`flex items-center justify-between px-3 py-2 border-t ${
                  isDark ? "border-gray-700" : "border-gray-100"
                }`}
              >
                <button
                  onClick={() => navigatePlace("prev")}
                  className={`flex items-center gap-1 text-xs ${
                    isDark ? "text-gray-400 hover:text-white" : "text-gray-500 hover:text-gray-900"
                  }`}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>
                <span className={`text-xs ${isDark ? "text-gray-500" : "text-gray-400"}`}>
                  {props.places.findIndex((p) => p.id === selectedPlace.id) + 1} of {props.places.length}
                </span>
                <button
                  onClick={() => navigatePlace("next")}
                  className={`flex items-center gap-1 text-xs ${
                    isDark ? "text-gray-400 hover:text-white" : "text-gray-500 hover:text-gray-900"
                  }`}
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </article>
          </div>
        )}
      </div>

      {/* Places List */}
      <div className={`border-t ${isDark ? "border-gray-700" : "border-gray-100"}`}>
        <div className="overflow-x-auto">
          <div className="flex gap-3 p-4">
            {props.places.map((place) => {
              const isSelected = widgetState?.selectedPlaceId === place.id;
              return (
                <button
                  key={place.id}
                  onClick={() => selectPlace(isSelected ? null : place.id)}
                  className={`flex-shrink-0 w-48 rounded-xl overflow-hidden border transition-all ${
                    isSelected
                      ? isDark
                        ? "border-blue-500 ring-2 ring-blue-500/20"
                        : "border-blue-500 ring-2 ring-blue-500/20"
                      : isDark
                      ? "border-gray-700 hover:border-gray-600"
                      : "border-gray-200 hover:border-gray-300"
                  } ${isDark ? "bg-gray-800" : "bg-white"}`}
                >
                  {/* Thumbnail */}
                  <div className="relative h-24 overflow-hidden">
                    {place.image ? (
                      <img
                        src={place.image}
                        alt={place.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div
                        className={`w-full h-full flex items-center justify-center ${
                          isDark ? "bg-gray-700" : "bg-gray-100"
                        }`}
                      >
                        <CategoryIcon category={place.category} />
                      </div>
                    )}
                    {/* Category badge */}
                    <span
                      className="absolute top-2 left-2 px-2 py-0.5 text-[10px] font-medium text-white rounded-full capitalize"
                      style={{ backgroundColor: categoryColors[place.category] }}
                    >
                      {place.category}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="p-2.5 text-left">
                    <h4
                      className={`font-medium text-sm truncate ${
                        isDark ? "text-white" : "text-gray-900"
                      }`}
                    >
                      {place.name}
                    </h4>
                    <div className="flex items-center gap-2 mt-1">
                      {place.rating && (
                        <div className="flex items-center gap-0.5">
                          <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                          <span
                            className={`text-xs ${isDark ? "text-gray-300" : "text-gray-600"}`}
                          >
                            {place.rating}
                          </span>
                        </div>
                      )}
                      {place.priceLevel && (
                        <span
                          className={`text-xs ${isDark ? "text-green-400" : "text-green-600"}`}
                        >
                          {place.priceLevel}
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
