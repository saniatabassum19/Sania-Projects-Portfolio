"use client";

import React, { useCallback, useState, useEffect } from "react";
import { generateProject } from "@/lib/generateProject";
import { flowToJson } from "@/lib/flowToJson";

import ReactFlow, {
    addEdge,
    Background,
    Controls,
    MiniMap,
    Connection,
    Edge,
    Node,
    useNodesState,
    useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";

let id = 0;
const getId = () => `node_${id++}`;

export default function FlowCanvas() {
    const [user, setUser] = useState<string | null>(null);
    const [usernameInput, setUsernameInput] = useState("");

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    const [projectName, setProjectName] = useState("");
    const [projects, setProjects] = useState<any[]>([]);
    const [plan, setPlan] = useState("");

    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [newNodeLabel, setNewNodeLabel] = useState("");
    const [newNodeType, setNewNodeType] = useState<"screen" | "event" | "condition">("screen");

    const [isPlaying, setIsPlaying] = useState(false);
    const [currentNodeId, setCurrentNodeId] = useState<string | null>(null);
    const [choices, setChoices] = useState<Edge[]>([]);

    // ------------------ NODE COLORS ------------------
    const getNodeStyle = (type: string) => {
        if (type === "screen") return { background: "#2563eb", color: "#fff" };
        if (type === "event") return { background: "#2563eb", color: "#fff" };
        return { background: "#2563eb", color: "#fff" };
    };

    const addNode = () => {
        if (!newNodeLabel) return;

        const style = getNodeStyle(newNodeType);

        const newNode: Node = {
            id: getId(),
            position: { x: Math.random() * 400, y: Math.random() * 400 },
            data: { label: newNodeLabel, type: newNodeType },
            style: {
                ...style,
                padding: "10px",
                borderRadius: "10px",
                fontSize: "14px",
            },
        };

        setNodes((nds) => [...nds, newNode]);
        setNewNodeLabel("");
    };

    const onConnect = useCallback((params: Connection) => {
        if (!params.source || !params.target) return;

        const newEdge: Edge = {
            ...params,
            source: params.source!,
            target: params.target!,
            id: `edge_${Math.random()}`,
            label: "edge",
            style: { stroke: "#aaa" },
        };

        setEdges((eds) => addEdge(newEdge, eds));
    }, []);


    // ------------------ PROJECTS ------------------
    const saveProject = () => {
        if (!projectName) return;

        const newProject = { name: projectName, nodes, edges };
        const updated = [...projects, newProject];

        setProjects(updated);
        localStorage.setItem("flowboard-projects", JSON.stringify(updated));
        setProjectName("");
    };

    const loadProject = (project: any) => {
        setNodes(project.nodes || []);
        setEdges(project.edges || []);
    };

    // ------------------ LOGIN ------------------
    const handleLogin = () => {
        if (!usernameInput) return;
        localStorage.setItem("flowboard-user", usernameInput);
        setUser(usernameInput);
    };

    const handleLogout = () => {
        localStorage.removeItem("flowboard-user");
        setUser(null);
    };

    // ------------------ PLAY MODE ------------------
    const getNextEdges = (nodeId: string) => {
        return edges.filter((e) => e.source === nodeId);
    };

    // ------------------ EFFECTS ------------------
    useEffect(() => {
        const savedUser = localStorage.getItem("flowboard-user");
        if (savedUser) setUser(savedUser);

        const saved = localStorage.getItem("flowboard-projects");
        if (saved) setProjects(JSON.parse(saved));
    }, []);

    // ------------------ LOGIN PAGE ------------------
    if (!user) {
        return (
            <div className="h-screen flex items-center justify-center bg-black text-white">
                <div className="bg-gray-900 p-8 rounded-xl w-80 text-center space-y-4">
                    <h1 className="text-2xl font-bold">Flowboard</h1>
                    <p className="text-sm text-gray-400">
                        Design your app flow visually and generate full-stack projects instantly.
                    </p>

                    <input
                        className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700"
                        placeholder="Enter your name"
                        value={usernameInput}
                        onChange={(e) => setUsernameInput(e.target.value)}
                    />

                    <button
                        onClick={handleLogin}
                        className="w-full py-2 bg-blue-600 rounded"
                    >
                        Enter
                    </button>
                </div>
            </div>
        );
    }

    // ------------------ MAIN UI ------------------
    return (
        <div className="h-screen flex flex-col bg-[#0f172a] text-white">

            {/* HEADER */}
            <div className="w-full h-12 bg-[#020617] flex justify-center items-center px-4 border-b border-gray-800">
                <h1 className="text-lg font-semibold">Flowboard</h1>
            </div>

            {/* MAIN CONTENT */}
            <div className="flex flex-1">

                {/* LEFT SIDEBAR */}
                <div className={`transition-all ${sidebarOpen ? "w-64" : "w-0"} bg-[#020617] p-4 space-y-4 overflow-hidden`}>
                    <h2 className="text-lg font-semibold">Flowboard</h2>

                    <div className="space-y-2">
                        <select
                            className="w-full bg-gray-800 p-2 rounded"
                            value={newNodeType}
                            onChange={(e) => setNewNodeType(e.target.value as any)}
                        >
                            <option value="screen">Screen</option>
                            <option value="event">Event</option>
                            <option value="condition">Condition</option>
                        </select>

                        <input
                            className="w-full p-2 bg-gray-800 rounded"
                            placeholder="Node name"
                            value={newNodeLabel}
                            onChange={(e) => setNewNodeLabel(e.target.value)}
                        />

                        <button onClick={addNode} className="w-full bg-blue-600 p-2 rounded">
                            Add Node
                        </button>
                    </div>

                    <div>
                        <input
                            className="w-full p-2 bg-gray-800 rounded mb-2"
                            placeholder="Project name"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                        />
                        <button onClick={saveProject} className="w-full bg-yellow-500 p-2 rounded">
                            Save Project
                        </button>
                    </div>

                    <div className="space-y-2">
                        {projects.map((p, i) => (
                            <button
                                key={i}
                                onClick={() => loadProject(p)}
                                className="w-full bg-gray-800 p-2 rounded text-left"
                            >
                                {p.name}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={async () => {
                            const json = flowToJson(nodes, edges);
                            const res = await fetch("/api/generate-plan", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify(json),
                            });
                            const data = await res.json();
                            setPlan(""); // clear first
                            setTimeout(() => {
                                setPlan(data.result);
                            }, 0);
                        }}
                        className="w-full bg-green-600 p-2 rounded"
                    >
                        Generate Plan
                    </button>

                    <button
                        onClick={() => {
                            const json = flowToJson(nodes, edges);
                            generateProject(json as any);
                        }}
                        className="w-full bg-purple-600 p-2 rounded"
                    >
                        Generate Project
                    </button>

                    <button onClick={handleLogout} className="w-full bg-red-500 p-2 rounded">
                        Logout
                    </button>
                </div>

                {/* CENTER CANVAS */}
                <div className="flex-1 relative">
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="absolute top-2 left-2 z-10 bg-black px-2 py-1 rounded"
                    >
                        ☰
                    </button>

                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}

                        onNodeClick={(e, node) => {
                            const newLabel = prompt("Edit node name", node.data.label);
                            if (!newLabel) return;

                            setNodes((nds) =>
                                nds.map((n) =>
                                    n.id === node.id
                                        ? { ...n, data: { ...n.data, label: newLabel } }
                                        : n
                                )
                            );
                        }}

                        onEdgeClick={(e, edge) => {
                            const newLabel = prompt("Edit edge label", edge.label as string);
                            if (!newLabel) return;

                            setEdges((eds) =>
                                eds.map((ed) =>
                                    ed.id === edge.id ? { ...ed, label: newLabel } : ed
                                )
                            );
                        }}
                    >

                        <Controls />
                        <Background color="#333" gap={16} />
                    </ReactFlow>
                </div>

                {/* RIGHT PANEL */}
                <div className="w-80 bg-[#020617] p-4 h-full overflow-y-auto">
                    <h2 className="font-semibold mb-2">AI Output</h2>
                    <div className="text-sm text-gray-300 whitespace-pre-wrap break-words max-h-full overflow-y-auto">
                        {plan || "Generate a plan to see output..."}
                    </div>
                </div>

            </div>
        </div>
    );
}