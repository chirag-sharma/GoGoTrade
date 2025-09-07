declare module 'react-plotly.js' {
  import { Component } from 'react';
  import { PlotParams } from 'plotly.js';

  export interface PlotProps extends Partial<PlotParams> {
    data: PlotParams['data'];
    layout?: Partial<PlotParams['layout']>;
    config?: Partial<PlotParams['config']>;
    frames?: PlotParams['frames'];
    revision?: number;
    onInitialized?: (figure: PlotParams, graphDiv: HTMLElement) => void;
    onPurge?: (figure: PlotParams, graphDiv: HTMLElement) => void;
    onError?: (err: Error) => void;
    onUpdate?: (figure: PlotParams, graphDiv: HTMLElement) => void;
    onRedraw?: () => void;
    onRelayout?: (eventData: any) => void;
    onRestyle?: (eventData: any) => void;
    onLegendClick?: (eventData: any) => boolean | void;
    onLegendDoubleClick?: (eventData: any) => boolean | void;
    onSliderChange?: (eventData: any) => void;
    onSliderStart?: (eventData: any) => void;
    onSliderEnd?: (eventData: any) => void;
    onAnimatingFrame?: (eventData: any) => void;
    onAnimationInterrupt?: (eventData: any) => void;
    onAutosize?: () => void;
    onBeforeExport?: () => void;
    onAfterExport?: () => void;
    onAfterPlot?: () => void;
    onButtonClicked?: (eventData: any) => void;
    onClickAnnotation?: (eventData: any) => void;
    onDeselect?: () => void;
    onDoubleClick?: () => void;
    onFramework?: () => void;
    onHover?: (eventData: any) => void;
    onSelected?: (eventData: any) => void;
    onSelecting?: (eventData: any) => void;
    onSunburstClick?: (eventData: any) => void;
    onTreemapClick?: (eventData: any) => void;
    onTransition?: () => void;
    onTransitionInterrupt?: () => void;
    onUnhover?: (eventData: any) => void;
    onWebGlContextLost?: () => boolean | void;
    divId?: string;
    className?: string;
    style?: React.CSSProperties;
    debug?: boolean;
    useResizeHandler?: boolean;
  }

  export default class Plot extends Component<PlotProps> {}
}
