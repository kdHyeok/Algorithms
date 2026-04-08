#include<iostream>

using namespace std;

long long arr[4'000'001];

int N, M, K, temp;
int caseA, inB;
long long inC;

void init(int index, int left, int right){
    if(left==right){
        cin>>arr[index];
        return;
    }
    int mid = left+(right-left)/2;
    
    init(index*2, left, mid);
    init(index*2+1, mid+1, right);

    arr[index] = arr[index*2]+arr[index*2+1];
}

void change(int index, int left, int right, int idx, long long val){
    if(idx<left || right<idx)
        return;
    
    if(left==right && left==idx){
        arr[index] = val;
        return;
    }

    int mid = left+(right-left)/2;

    if(idx<=mid){
        change(index*2, left, mid, idx, val);
        arr[index] = arr[index*2]+arr[index*2+1];
    }
    else{
        change(index*2+1, mid+1, right, idx, val);
        arr[index] = arr[index*2]+arr[index*2+1];
    }
}

long long rangeSum(int index, int left, int right, int st, int ed){
    if(ed<left || right<st)
        return 0;
    
    if((left==right) || (st<=left && right<=ed))
        return arr[index];

    int mid = left+(right-left)/2;

    long long leftSum = rangeSum(index*2, left, mid, st, ed);
    long long rightSum = rangeSum(index*2+1, mid+1, right, st, ed);

    return leftSum+rightSum;
}

int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout.tie(NULL);
    //freopen("sample_input.txt","r",stdin);

    cin>>N>>M>>K;
    init(1,1,N);
    for (int i = 1; i<=(M+K);i++){
        cin>>caseA>>inB>>inC;
        if(caseA==1){
            change(1, 1, N, inB, inC);
            arr[1] = arr[2]+arr[3];
            int de = 1;
        }
        else{
            cout<<rangeSum(1,1,N,inB,(int)inC)<<'\n';
        }
    }
}