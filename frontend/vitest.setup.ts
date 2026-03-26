import "@testing-library/jest-dom/vitest";

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

const canvas2dStub = {
  fillRect: () => {},
  clearRect: () => {},
  getImageData: () => ({ data: new Uint8ClampedArray(0), width: 0, height: 0 }),
  putImageData: () => {},
  createImageData: () => ({ data: new Uint8ClampedArray(0), width: 0, height: 0 }),
  setTransform: () => {},
  drawImage: () => {},
  save: () => {},
  fillText: () => {},
  restore: () => {},
  beginPath: () => {},
  moveTo: () => {},
  lineTo: () => {},
  closePath: () => {},
  stroke: () => {},
  translate: () => {},
  scale: () => {},
  rotate: () => {},
  arc: () => {},
  fill: () => {},
  measureText: () => ({ width: 0 }),
  transform: () => {},
  rect: () => {},
  clip: () => {},
  canvas: { width: 300, height: 150 },
};

HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, type: string) {
  if (type === "2d") return canvas2dStub as unknown as CanvasRenderingContext2D;
  return null;
};

globalThis.ResizeObserver = class ResizeObserverMock {
  constructor(private readonly cb: ResizeObserverCallback) {}

  observe(target: Element) {
    const rect = target.getBoundingClientRect();
    queueMicrotask(() => {
      this.cb(
        [
          {
            target,
            contentRect: rect,
            borderBoxSize: [],
            contentBoxSize: [],
            devicePixelContentBoxSize: [],
          } as ResizeObserverEntry,
        ],
        this,
      );
    });
  }

  unobserve() {}

  disconnect() {}
};
