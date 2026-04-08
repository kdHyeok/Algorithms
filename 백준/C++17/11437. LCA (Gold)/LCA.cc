#include <iostream>
#include <vector>

using namespace std;

int parent[50001];
bool visited[50001];
vector<int> adj[50001];
vector<pair<int, int>> queries[50001];
int answers[100001];

// 표준 Path Compression
int find(int tar) {
    if (tar == parent[tar]) return tar;
    return parent[tar] = find(parent[tar]);
}

void LCA(int curr) {
    visited[curr] = true;

    for (int next : adj[curr]) {
        if (!visited[next]) {
            LCA(next);
            // 자식 탐색 완료 후, 자식의 부모를 현재 노드로 설정
            parent[next] = curr; 
        }
    }

    // 현재 노드와 관련된 쿼리 처리
    for (auto& q : queries[curr]) {
        int target = q.first;
        int queryIdx = q.second;

        if (visited[target]) {
            // target이 속한 집합의 최상단 부모가 LCA
            answers[queryIdx] = find(target);
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N, M;
    if (!(cin >> N)) return 0;

    for (int i = 1; i <= N; i++) parent[i] = i;

    for (int i = 0; i < N - 1; i++) {
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    if (!(cin >> M)) return 0;
    for (int i = 0; i < M; i++) {
        int u, v;
        cin >> u >> v;
        queries[u].push_back({ v, i });
        queries[v].push_back({ u, i });
    }

    LCA(1);

    for (int i = 0; i < M; i++) {
        cout << answers[i] << "\n";
    }

    return 0;
}