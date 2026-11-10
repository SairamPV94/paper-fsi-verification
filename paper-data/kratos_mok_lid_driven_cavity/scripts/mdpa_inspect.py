#!/usr/bin/env python3
"""Summarise a Kratos .mdpa file: element/condition blocks and the bounding box of
the nodes in every SubModelPart. Pure Python, no Kratos needed.

Usage: python mdpa_inspect.py file.mdpa
"""
import sys
import re


def read_mdpa(path):
    nodes = {}
    blocks = []          # (kind, type name, count)
    smp = {}             # name -> set of node ids
    stack = []
    section = None
    count = 0
    with open(path) as f:
        for raw in f:
            line = raw.split("//")[0].strip()
            if not line:
                continue
            if line.startswith("Begin "):
                words = line.split()
                kind = words[1]
                if kind == "SubModelPart":
                    stack.append(words[2])
                    smp.setdefault("/".join(stack), set())
                    section = "SubModelPart"
                elif kind in ("Nodes", "Elements", "Conditions"):
                    section = kind
                    count = 0
                    blocks_name = words[2] if len(words) > 2 else ""
                elif kind == "SubModelPartNodes":
                    section = "SubModelPartNodes"
                else:
                    section = kind
                continue
            if line.startswith("End "):
                kind = line.split()[1]
                if kind == "SubModelPart":
                    stack.pop()
                elif kind in ("Elements", "Conditions"):
                    blocks.append((kind, blocks_name, count))
                elif kind == "Nodes":
                    blocks.append(("Nodes", "", count))
                section = "SubModelPart" if stack else None
                continue
            if section == "Nodes":
                i, x, y, z = line.split()[:4]
                nodes[int(i)] = (float(x), float(y), float(z))
                count += 1
            elif section in ("Elements", "Conditions"):
                count += 1
            elif section == "SubModelPartNodes":
                smp["/".join(stack)].add(int(line.split()[0]))
    return nodes, blocks, smp


def main():
    nodes, blocks, smp = read_mdpa(sys.argv[1])
    for kind, name, n in blocks:
        print(f"{kind:10s} {name:28s} {n}")
    for name, ids in smp.items():
        if not ids:
            print(f"{name:55s} no nodes")
            continue
        xs = [nodes[i][0] for i in ids]
        ys = [nodes[i][1] for i in ids]
        print(f"{name:55s} {len(ids):5d} nodes  x [{min(xs):.5f}, {max(xs):.5f}]"
              f"  y [{min(ys):.5f}, {max(ys):.5f}]")


if __name__ == "__main__":
    main()
