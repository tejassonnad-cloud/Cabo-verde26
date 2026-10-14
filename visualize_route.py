"""Animate a solved route over an edge CSV using matplotlib and networkx.

Usage: python visualize_route.py --edges flights.csv --path route.csv
The route CSV is produced by budget_traveller.py/ BudgetTraveller.java --csv-out.
Coupon flights are gold; each animation frame reports accumulated cost/stops.
"""
import argparse
import csv
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation

def rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--edges",required=True,help="CSV columns from,to,price")
    p.add_argument("--path",required=True,help="solver path CSV")
    p.add_argument("--interval",type=int,default=800)
    args=p.parse_args()
    all_edges=rows(args.edges); route=rows(args.path)
    g=nx.DiGraph()
    for e in all_edges:g.add_edge(int(e["from"]),int(e["to"]),price=int(e["price"]))
    pos=nx.spring_layout(g,seed=7)
    fig,ax=plt.subplots(figsize=(10,7))
    route_pairs=[(int(e["from"]),int(e["to"])) for e in route]
    def draw(frame):
        ax.clear(); done=route[:frame]
        coupon_pairs=[(int(e["from"]),int(e["to"])) for e in done if e.get("coupon_used")=="x"]
        done_pairs=[(int(e["from"]),int(e["to"])) for e in done]
        nx.draw_networkx_nodes(g,pos,node_color="#dce8f5",node_size=900,ax=ax)
        nx.draw_networkx_labels(g,pos,ax=ax)
        nx.draw_networkx_edges(g,pos,edge_color="#b9c2cc",arrows=True,arrowsize=18,connectionstyle="arc3,rad=0.08",ax=ax)
        if done_pairs:nx.draw_networkx_edges(g,pos,edgelist=done_pairs,edge_color="#2878c8",width=3,arrows=True,arrowsize=22,connectionstyle="arc3,rad=0.08",ax=ax)
        if coupon_pairs:nx.draw_networkx_edges(g,pos,edgelist=coupon_pairs,edge_color="gold",width=4,arrows=True,arrowsize=24,connectionstyle="arc3,rad=0.08",ax=ax)
        labels={(u,v):str(d["price"]) for u,v,d in g.edges(data=True)}
        nx.draw_networkx_edge_labels(g,pos,edge_labels=labels,font_size=8,ax=ax)
        cost=sum(int(e["price"])//2 if e.get("coupon_used")=="x" else int(e["price"]) for e in done)
        ax.set_title(f"Flight {len(done)}/{len(route)}   Cost: {cost}   Stops used: {max(0,len(done)-1)}")
        ax.axis("off")
    anim=FuncAnimation(fig,draw,frames=len(route)+1,interval=args.interval,repeat=False)
    # Keep a reference alive for GUI backends; show is interactive.
    plt.tight_layout();plt.show()

if __name__=="__main__": main()
