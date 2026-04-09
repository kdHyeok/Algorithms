# [Unrated] [모의 SW 역량테스트] 보호 필름 - 2112 

[문제 링크](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV5V1SYKAaUDFAWu) 

### 성능 요약
메모리: 5,976 KB, 시간: 1,089 ms, 코드길이: 1,302 Bytes

### 분류 

DFS

### 제출 일자
2026-04-09 03:37

### 소감
- 가지치기가 중요한 문제.
```cpp
vector<vector<int>> map(21, vector<int>(21, 0));
vector<vector<int>> copy_map(21, vector<int>(21, 0));
:
:
void dfs(int& ans, int idx, int cnt) {
	if (ans <= cnt || cnt > K) return;
	
	// 검사
	if (idx == D) {
		if (test()) {
			if (ans > cnt)
				ans = cnt;
		}
		return;
	}
```

