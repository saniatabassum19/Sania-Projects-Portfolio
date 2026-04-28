export type NodeType = "screen" | "event" | "condition";

export type FlowNode = {
    id: string;
    data: {
        label: string;
        type: NodeType;
    };
};

export type FlowEdge = {
    id: string;
    source: string;
    target: string;
    label?: string;
};