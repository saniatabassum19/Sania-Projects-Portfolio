import { Node, Edge } from "reactflow";

export function flowToJson(nodes: Node[], edges: Edge[]) {
    return {
        nodes: nodes.map((node) => ({
            id: node.id,
            label: node.data?.label || "",
            type: node.data?.type || "",
        })),
        edges: edges.map((edge) => ({
            from: edge.source,
            to: edge.target,
            label: edge.label || "",
            edges: edges.map((edge) => ({
                from: edge.source,
                to: edge.target,
                label: String(edge.label || ""),
            })),
        })),
    };
}