/**
 * CesiumJS Globe Widget
 *
 * Interactive 3D globe with OpenStreetMap tiles and geocoding.
 * CesiumJS is loaded dynamically from CDN (not bundled).
 * Ported from modelcontextprotocol/ext-apps map-server.
 */

import { useEffect, useRef } from "react";
import { useWidgetProps } from "../use-widget-props";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare let Cesium: any;

const CESIUM_VERSION = "1.123";
const CESIUM_BASE_URL = `https://cesium.com/downloads/cesiumjs/releases/${CESIUM_VERSION}/Build/Cesium`;

interface ToolOutput {
  west: number;
  south: number;
  east: number;
  north: number;
  label?: string;
}

const defaultProps: ToolOutput = {
  west: -0.5,
  south: 51.3,
  east: 0.3,
  north: 51.7,
};

async function loadCesium(): Promise<void> {
  if (typeof Cesium !== "undefined") return;

  // Load CSS
  const cssLink = document.createElement("link");
  cssLink.rel = "stylesheet";
  cssLink.href = `${CESIUM_BASE_URL}/Widgets/widgets.css`;
  document.head.appendChild(cssLink);

  // Load JS
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = `${CESIUM_BASE_URL}/Cesium.js`;
    script.onload = () => {
      (window as any).CESIUM_BASE_URL = CESIUM_BASE_URL;
      resolve();
    };
    script.onerror = () => reject(new Error("Failed to load CesiumJS from CDN"));
    document.head.appendChild(script);
  });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function initViewer(container: HTMLElement): any {
  Cesium.Ion.defaultAccessToken = undefined;
  Cesium.Camera.DEFAULT_VIEW_RECTANGLE = Cesium.Rectangle.fromDegrees(-130, 20, -60, 55);

  const viewer = new Cesium.Viewer(container, {
    baseLayer: false,
    geocoder: false,
    baseLayerPicker: false,
    animation: false,
    timeline: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    terrainProvider: undefined,
    contextOptions: {
      webgl: { preserveDrawingBuffer: true, alpha: true },
    },
    useBrowserRecommendedResolution: false,
  });

  viewer.scene.globe.show = true;
  viewer.scene.globe.enableLighting = false;
  viewer.scene.globe.baseColor = Cesium.Color.DARKSLATEGRAY;
  viewer.scene.requestRenderMode = false;
  viewer.canvas.style.imageRendering = "auto";
  viewer.scene.postProcessStages.fxaa.enabled = false;

  // Add OpenStreetMap tiles
  const osmProvider = new Cesium.UrlTemplateImageryProvider({
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    minimumLevel: 0,
    maximumLevel: 19,
    credit: new Cesium.Credit(
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      true,
    ),
  });
  viewer.imageryLayers.addImageryProvider(osmProvider);

  // Force initial renders for sandboxed iframe contexts
  let renderCount = 0;
  const initialRenderLoop = () => {
    viewer.render();
    viewer.scene.requestRender();
    renderCount++;
    if (renderCount < 20) {
      setTimeout(initialRenderLoop, 50);
    }
  };
  initialRenderLoop();

  return viewer;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function flyToBbox(viewer: any, bbox: ToolOutput): void {
  const centerLon = (bbox.west + bbox.east) / 2;
  const centerLat = (bbox.south + bbox.north) / 2;
  const lonSpan = Math.abs(bbox.east - bbox.west);
  const latSpan = Math.abs(bbox.north - bbox.south);
  const maxSpan = Math.max(lonSpan, latSpan);
  const height = Math.max(100000, maxSpan * 111000 * 5);
  const actualHeight = Math.max(height, 500000);

  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(centerLon, centerLat, actualHeight),
    orientation: {
      heading: 0,
      pitch: Cesium.Math.toRadians(-90),
      roll: 0,
    },
  });
}

export default function App() {
  const props = useWidgetProps<ToolOutput>(defaultProps);
  const containerRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const viewerRef = useRef<any>(null);
  const loadingRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);

  // Initialize Cesium
  useEffect(() => {
    if (!containerRef.current || initializedRef.current) return;
    initializedRef.current = true;

    (async () => {
      await loadCesium();
      const viewer = initViewer(containerRef.current!);
      viewerRef.current = viewer;

      // Fly to initial bbox
      flyToBbox(viewer, props);

      // Hide loading
      if (loadingRef.current) {
        loadingRef.current.style.display = "none";
      }
    })();

    return () => {
      if (viewerRef.current) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Update view when props change
  useEffect(() => {
    if (viewerRef.current && props.west !== defaultProps.west) {
      flyToBbox(viewerRef.current, props);
    }
  }, [props.west, props.south, props.east, props.north]);

  return (
    <div style={styles.wrapper}>
      <div ref={containerRef} style={styles.container} />
      <div ref={loadingRef} style={styles.loading}>
        Loading globe...
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    position: "relative",
    width: "100%",
    height: 400,
  },
  container: {
    width: "100%",
    height: "100%",
  },
  loading: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "rgba(0, 0, 0, 0.5)",
    color: "white",
    fontSize: 16,
    zIndex: 10,
  },
};
