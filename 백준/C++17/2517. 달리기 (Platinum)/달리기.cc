#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// MAX_N: 참가하는 선수의 최대 수
// 목적/이유: 세그먼트 트리의 메모리를 데이터 개수에 비례하도록 안전하게 사전 할당하기 위함.
// 사용법: 배열 크기를 정할 때 N의 최댓값인 500,000을 기준으로 설정한다.
const int MAX_N = 500000;

// tree: 누적된 선수들의 숫자를 구간별로 저장하는 세그먼트 트리
// 목적/이유: 특정 실력 구간에 몇 명의 선수가 존재하는지 O(\log N)만에 쿼리하고 업데이트하기 위함.
// 사용법: 크기는 N의 4배로 선언. 값(실력)이 10억이라도, 압축을 거치면 인덱스는 최대 50만 내외에서 안전하게 돈다.
vector<int> tree(MAX_N * 4, 0);

// update(): 특정 실력(압축된 인덱스)을 가진 선수가 지나갔음을 트리에 기록하는 함수
// 목적/이유: 나보다 뒤에 뛰는 선수가 나를 쿼리할 때 나의 존재를 카운트할 수 있도록 O(\log N)만에 트리에 누적하기 위함.
// 사용법: node(현재 트리 위치), start~end(트리가 담당하는 실력 순위 구간), idx(현재 선수의 압축된 실력 순위)를 받아 해당 경로에 1을 더한다.
void update(int node, int start, int end, int idx) {
    if (idx < start || end < idx) return;
    tree[node] += 1;
    if (start != end) {
        int mid = (start + end) / 2;
        update(node * 2, start, mid, idx);
        update(node * 2 + 1, mid + 1, end, idx);
    }
}

// query(): 1부터 target_idx(내 실력-1)까지의 구간에 속한 선수의 총합을 구하는 함수
// 목적/이유: 내 앞을 달리고 있는 선수들 중, 나보다 실력이 낮은(압축 순위가 낮은) 선수의 수를 O(\log N)만에 파악하기 위함.
// 사용법: node, start, end와 함께 left=1, right=내 실력-1 을 넘겨 구간 내 누적 인원수를 반환받는다.
int query(int node, int start, int end, int left, int right) {
    if (left > end || right < start) return 0;
    if (left <= start && end <= right) return tree[node];
    int mid = (start + end) / 2;
    return query(node * 2, start, mid, left, right) + 
           query(node * 2 + 1, mid + 1, end, left, right);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // N: 참가 선수의 수
    // 목적/이유: 반복 횟수 및 배열 크기를 통제.
    // 사용법: 입력을 받아 검증에 사용.
    int N;
    cin >> N;

    // raw_data: 선수들의 원래 달리는 순서와 진짜 실력(최대 10억)을 보관하는 배열
    // 목적/이유: 압축을 수행한 뒤에도 원래 달리는 순서대로 로직을 처리해야 하므로 원본을 훼손 없이 유지하기 위함.
    // 사용법: N번 반복하며 실력 값을 차례대로 채워 넣는다.
    vector<int> raw_data(N);
    for (int i = 0; i < N; i++) {
        cin >> raw_data[i];
    }

    // sorted_data: 좌표 압축을 위한 징검다리(순위표) 배열
    // 목적/이유: 10억짜리 실력을 1등, 2등 같은 조밀한 인덱스로 맵핑하기 위함.
    // 사용법: 원본을 복사하고 정렬(sort)한다. 문제에서 모든 실력이 다르다고 했으므로 unique는 생략해도 무방하나, 정석대로 남겨둔다.
    vector<int> sorted_data = raw_data;
    sort(sorted_data.begin(), sorted_data.end());

    // 달리는 순서대로 한 명씩 처리
    for (int i = 0; i < N; i++) {
        // rank_idx: 현재 선수의 거대한 실력이 정렬된 기준표에서 몇 번째 순위인지 찾은 결과값
        // 목적/이유: 메모리가 터지지 않도록 거대 값을 1~N 사이의 안전한 트리 인덱스로 변환하기 위함. (세그먼트 트리를 1-based로 쓰기 위해 +1 추가)
        // 사용법: lower_bound 이진 탐색으로 순위를 빠르게 도출한다.
        int rank_idx = lower_bound(sorted_data.begin(), sorted_data.end(), raw_data[i]) - sorted_data.begin() + 1;

        // overtaken: 내 앞에 달리는 사람 중, 나보다 실력이 낮아(1 ~ rank_idx-1) 내가 앞지를 수 있는 사람의 수
        // 목적/이유: 내 현재 등수에서 뺄셈을 하기 위한 핵심 지표를 추출하기 위함.
        // 사용법: 세그먼트 트리에 구간 합 쿼리를 날린다.
        int overtaken = query(1, 1, N, 1, rank_idx - 1);

        // best_rank: 현재 내가 낼 수 있는 최고의 등수
        // 목적/이유: 문제에서 요구하는 최종 정답 도출. (현재 위치(i+1) - 앞지른 사람 수)
        // 사용법: 바로 연산하여 콘솔에 출력한다.
        int best_rank = (i + 1) - overtaken;
        cout << best_rank << "\n";

        // update(): 처리가 끝난 내 실력을 트리에 기록
        // 목적/이유: 내가 처리되었으므로, 내 뒤에 달리는 다음 선수가 나를 쿼리 대상에 포함시킬 수 있도록 장부에 추가하기 위함.
        // 사용법: 현재 선수의 압축된 순위(rank_idx) 위치에 1을 누적한다.
        update(1, 1, N, rank_idx);
    }

    return 0;
}