#include <iostream>
#include <string>

using namespace std;

const int N = 600'005;
char dat[N];
int pre[N], nxt[N];
int unused[N];
int unId = 0, tail = 0;

void init() {
	fill(dat, dat + N, -1);
	fill(pre, pre + N, -1);
	fill(nxt, nxt + N, -1);
	unused[0] = 1;
}

void insert(int adrr, int val) {
	dat[unused[unId]] = val;
	pre[unused[unId]] = adrr;
	nxt[unused[unId]] = nxt[adrr];
	if (nxt[adrr] != -1) pre[nxt[adrr]] = unused[unId];
	else tail = unused[unId];
	nxt[adrr] = unused[unId];
	if(unId==0) unused[0]++;
	else unId--;
	
}

void erase(int adrr) {
	nxt[pre[adrr]] = nxt[adrr];
	if (nxt[adrr] != -1) pre[nxt[adrr]] = pre[adrr];
	nxt[adrr] = -1;
	if (tail == adrr) tail = pre[adrr];
	pre[adrr] = -1;
	unused[++unId] = adrr;
}

int main() {
	ios::sync_with_stdio(0);
	cin.tie(0);
	init();
	string input;
	cin >> input;
	int cur = 0;
	for (auto& s : input)
	{
		insert(cur, s);
		cur = nxt[cur];
	}
	int m;
	cin >> m;
	char cmd, x;
	while (m--)
	{
		cin >> cmd;
		switch (cmd)
		{
		case 'L':
		{
			if (pre[cur] != -1) cur = pre[cur];
			continue;
		}
		case 'D':
		{
			if (nxt[cur] != -1) cur = nxt[cur];
			continue;
		}
		case 'B':
		{
			if (pre[cur] != -1) {
				int precur = pre[cur];
				erase(cur);
				cur = precur;
			}
			continue;
		}
		case 'P':
		{
			cin >> x;
			insert(cur, x);
			cur = nxt[cur];
			continue;
		}
		}
	}

	cur = nxt[0];
	while (cur != -1)
	{
		cout << dat[cur];
		cur = nxt[cur];
	}
	return 0;
}