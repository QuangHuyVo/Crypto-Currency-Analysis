/** Intervals that support crosshair click → as_of prediction (align with backend AS_OF_PREDICTION_INTERVALS). */
export const AS_OF_PREDICTION_INTERVALS = ["4h", "1d", "1w", "1M"] as const;

export type AsOfPredictionInterval = (typeof AS_OF_PREDICTION_INTERVALS)[number];

export function isAsOfPredictionInterval(iv: string): iv is AsOfPredictionInterval {
  return (AS_OF_PREDICTION_INTERVALS as readonly string[]).includes(iv);
}
