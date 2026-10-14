import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Budget Traveller with Coupons.
 * Stdin: N M K C, then M triples u v price (1-indexed).
 * CSV: --input-csv edges.csv --n N --k K --coupons C; columns from,to,price.
 * Prints minimum cost/-1. --csv-out writes chosen path; coupon_used/path_mark
 * contain x markers on the route edges.
 */
public class BudgetTraveller {
    static final class Edge { int to, price; Edge(int t, int p) { to=t; price=p; } }
    static final class State implements Comparable<State> {
        long cost; int city, flights, used;
        State(long c,int v,int f,int u){cost=c;city=v;flights=f;used=u;}
        public int compareTo(State o){return Long.compare(cost,o.cost);}
    }
    static final class Prev { int city, flights, used, price; boolean coupon;
        Prev(int c,int f,int u,int p,boolean x){city=c;flights=f;used=u;price=p;coupon=x;}
    }
    static final class RouteRow { int from,to,price; boolean coupon;
        RouteRow(int a,int b,int p,boolean c){from=a;to=b;price=p;coupon=c;}
    }
    static final class Result { long cost; List<RouteRow> route;
        Result(long c,List<RouteRow> r){cost=c;route=r;}
    }

    static Result solve(int n,int k,int coupons,List<int[]> input) {
        if(n<1||k<0||coupons<0) throw new IllegalArgumentException("N must be positive; K and C non-negative");
        @SuppressWarnings("unchecked") List<Edge>[] g=new List[n+1];
        for(int i=0;i<=n;i++)g[i]=new ArrayList<>();
        for(int[] e:input){if(e[0]<1||e[0]>n||e[1]<1||e[1]>n||e[2]<0)throw new IllegalArgumentException("invalid edge");g[e[0]].add(new Edge(e[1],e[2]));}
        int maxFlights=k+1; coupons=Math.min(coupons,maxFlights); // extra coupons cannot be used
        long[][][] d=new long[n+1][maxFlights+1][coupons+1];
        for(long[][] a:d)for(long[] b:a)Arrays.fill(b,Long.MAX_VALUE);
        Prev[][][] prev=new Prev[n+1][maxFlights+1][coupons+1];
        d[1][0][0]=0;
        PriorityQueue<State> pq=new PriorityQueue<>();pq.add(new State(0,1,0,0));
        State goal=null;
        while(!pq.isEmpty()){
            State s=pq.poll(); if(s.cost!=d[s.city][s.flights][s.used])continue;
            if(s.city==n){goal=s;break;} if(s.flights==maxFlights)continue;
            for(Edge e:g[s.city]){
                relax(e.to,s.flights+1,s.used,s.cost+e.price,s,e,false,d,prev,pq);
                if(s.used<coupons)relax(e.to,s.flights+1,s.used+1,s.cost+e.price/2,s,e,true,d,prev,pq);
            }
        }
        if(goal==null)return new Result(-1,new ArrayList<>());
        List<RouteRow> route=new ArrayList<>();int v=goal.city,f=goal.flights,u=goal.used;
        while(f>0){Prev p=prev[v][f][u];route.add(new RouteRow(p.city,v,p.price,p.coupon));v=p.city;f=p.flights;u=p.used;}
        Collections.reverse(route);return new Result(goal.cost,route);
    }
    static void relax(int v,int f,int u,long cost,State s,Edge e,boolean coupon,long[][][] d,Prev[][][] prev,PriorityQueue<State> pq){
        if(cost<d[v][f][u]){d[v][f][u]=cost;prev[v][f][u]=new Prev(s.city,s.flights,s.used,e.price,coupon);pq.add(new State(cost,v,f,u));}
    }
    static List<int[]> readCsv(String file)throws IOException{
        List<int[]> out=new ArrayList<>();List<String> lines=Files.readAllLines(Paths.get(file));if(lines.isEmpty())throw new IllegalArgumentException("empty CSV");
        String[] h=lines.get(0).replace("\uFEFF","").split(",",-1);int fi=-1,ti=-1,pi=-1;
        for(int i=0;i<h.length;i++){String x=h[i].trim();if(x.equals("from"))fi=i;if(x.equals("to"))ti=i;if(x.equals("price"))pi=i;}
        if(fi<0||ti<0||pi<0)throw new IllegalArgumentException("CSV needs from,to,price columns");
        for(int i=1;i<lines.size();i++){if(lines.get(i).trim().isEmpty())continue;String[] a=lines.get(i).split(",",-1);out.add(new int[]{Integer.parseInt(a[fi].trim()),Integer.parseInt(a[ti].trim()),Integer.parseInt(a[pi].trim())});}
        return out;
    }
    static void writeCsv(String file,List<RouteRow> route)throws IOException{
        try(BufferedWriter w=Files.newBufferedWriter(Paths.get(file))){w.write("from,to,price,coupon_used,path_mark\n");for(RouteRow r:route)w.write(r.from+","+r.to+","+r.price+","+(r.coupon?"x":"")+",x\n");}
    }
    static int[] readInts()throws IOException{String s=new String(System.in.readAllBytes()).trim();if(s.isEmpty())throw new IllegalArgumentException("empty input");String[] a=s.split("\\s+");int[] z=new int[a.length];for(int i=0;i<a.length;i++)z[i]=Integer.parseInt(a[i]);return z;}
    public static void main(String[] args)throws Exception{
        Map<String,String> opt=new HashMap<>();for(int i=0;i<args.length;i++){if(i+1>=args.length)throw new IllegalArgumentException("missing value for "+args[i]);opt.put(args[i],args[++i]);}
        int n,k,c;List<int[]> edges;
        if(opt.containsKey("--input-csv")){n=Integer.parseInt(opt.get("--n"));k=Integer.parseInt(opt.get("--k"));c=Integer.parseInt(opt.get("--coupons"));edges=readCsv(opt.get("--input-csv"));}
        else{int[] a=readInts();if(a.length<4)throw new IllegalArgumentException("expected N M K C and edges");n=a[0];int m=a[1];k=a[2];c=a[3];if(a.length!=4+3*m)throw new IllegalArgumentException("edge count mismatch");edges=new ArrayList<>();for(int i=4;i<a.length;i+=3)edges.add(new int[]{a[i],a[i+1],a[i+2]});}
        Result r=solve(n,k,c,edges);System.out.println(r.cost);if(opt.containsKey("--csv-out"))writeCsv(opt.get("--csv-out"),r.route);
    }
}
