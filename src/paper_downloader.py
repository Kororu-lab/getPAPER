import arxiv
import os
import requests
import time
import json
from datetime import datetime, timedelta
from tqdm import tqdm
from pathlib import Path

class ArxivPaperDownloader:
    def __init__(self):
        self.base_dir = Path("data/pdf")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = Path("data/progress.json")
        self.total_downloaded = 0
        self.total_errors = 0
        self.last_search_time = None
        self.min_search_interval = 3  # 최소 검색 간격 (초)
        
    def load_progress(self):
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data['last_completed_month'])
            except Exception as e:
                print(f"진행 상황 로드 중 오류: {e}")
        return None
    
    def save_progress(self, date):
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump({'last_completed_month': date.isoformat()}, f)
        except Exception as e:
            print(f"진행 상황 저장 중 오류: {e}")
    
    def download_paper(self, url, filename):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                
                with open(filename, 'wb') as file, tqdm(
                    desc=os.path.basename(filename),
                    total=total_size,
                    unit='iB',
                    unit_scale=True
                ) as pbar:
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        pbar.update(size)
                return True
            except Exception as e:
                print(f"다운로드 중 오류 발생: {e}")
                retry_count += 1
                if retry_count == max_retries:
                    return False
                time.sleep(2)
        return False
    
    def wait_for_api_limit(self):
        if self.last_search_time is not None:
            elapsed = time.time() - self.last_search_time
            if elapsed < self.min_search_interval:
                time.sleep(self.min_search_interval - elapsed)
        self.last_search_time = time.time()
    
    def get_month_range(self, date):
        # 해당 월의 첫 날과 마지막 날을 반환
        first_day = date.replace(day=1)
        if date.month == 12:
            last_day = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
        return first_day, last_day
    
    def fetch_papers(self, start_date=None, batch_size=10000):
        if start_date is None:
            start_date = datetime(2024, 12, 31)
            
        # 이전 진행 상황 로드
        last_completed = self.load_progress()
        if last_completed:
            print(f"이전 진행 상황 발견: {last_completed.strftime('%Y-%m')}까지 완료")
            # 이전 달부터 시작
            if last_completed.month == 1:
                current_date = last_completed.replace(year=last_completed.year - 1, month=12)
            else:
                current_date = last_completed.replace(month=last_completed.month - 1)
        else:
            current_date = start_date
        
        with tqdm(desc="전체 진행률", unit="월") as pbar:
            while True:  # 무한 루프
                first_day, last_day = self.get_month_range(current_date)
                
                # 검색 쿼리 설정
                categories = ['cs.AI', 'cs.CV']
                query = ' OR '.join(f'cat:{cat}' for cat in categories)
                query += f' AND submittedDate:[{first_day.strftime("%Y%m%d")}0000 TO {last_day.strftime("%Y%m%d")}2359]'
                
                print(f"\n\n=== {first_day.strftime('%Y-%m')} 월 논문 검색 중 ===")
                print(f"검색 기간: {first_day.strftime('%Y-%m-%d')} ~ {last_day.strftime('%Y-%m-%d')}")
                print(f"검색 쿼리: {query}")
                
                # API 제한 대기
                self.wait_for_api_limit()
                
                # arXiv API 클라이언트 설정
                client = arxiv.Client()
                
                try:
                    # 논문 검색
                    search = arxiv.Search(
                        query=query,
                        max_results=batch_size,
                        sort_by=arxiv.SortCriterion.SubmittedDate,
                        sort_order=arxiv.SortOrder.Descending
                    )
                    
                    papers = list(client.results(search))
                    print(f"검색된 논문 수: {len(papers)}")
                    
                    # 검색 결과가 배치 크기와 같으면 추가 검색 필요
                    if len(papers) == batch_size:
                        print("주의: 검색 결과가 배치 크기와 같습니다. 일부 논문이 누락되었을 수 있습니다.")
                        print("이 경우, 해당 월을 더 작은 기간으로 나누어 검색할 수 있습니다.")
                    
                    if papers:
                        with tqdm(total=len(papers), desc="논문 다운로드", unit="편") as paper_pbar:
                            for paper in papers:
                                try:
                                    pdf_url = paper.pdf_url
                                    paper_id = paper.get_short_id()
                                    filename = f"{paper_id.replace('/', '_')}.pdf"
                                    filepath = self.base_dir / filename
                                    
                                    print(f"\n제목: {paper.title}")
                                    print(f"ID: {paper_id}")
                                    print(f"카테고리: {', '.join(paper.categories)}")
                                    print(f"게시일: {paper.published}")
                                    
                                    if not filepath.exists():
                                        if self.download_paper(pdf_url, filepath):
                                            self.total_downloaded += 1
                                            print("다운로드 성공")
                                        else:
                                            self.total_errors += 1
                                            print("다운로드 실패")
                                    else:
                                        print("이미 존재하는 파일")
                                    
                                    paper_pbar.update(1)
                                    time.sleep(1)  # API 제한 방지
                                    
                                except Exception as e:
                                    print(f"논문 처리 중 오류: {e}")
                                    self.total_errors += 1
                                    continue
                    
                except Exception as e:
                    print(f"검색 중 오류 발생: {e}")
                    time.sleep(60)  # 오류 발생 시 1분 대기
                    continue
                
                print(f"\n=== 진행 상황 ===")
                print(f"총 다운로드: {self.total_downloaded}개")
                print(f"총 실패: {self.total_errors}개")
                
                # 현재 달이 성공적으로 완료되었을 때만 진행 상황 저장
                if self.total_errors == 0:
                    self.save_progress(current_date)
                
                # Move to previous month
                if current_date.month == 1:
                    current_date = current_date.replace(year=current_date.year - 1, month=12)
                else:
                    current_date = current_date.replace(month=current_date.month - 1)
                
                pbar.update(1)
                time.sleep(3)  # 다음 달 검색 전 대기

if __name__ == "__main__":
    downloader = ArxivPaperDownloader()
    # 2024년 12월부터 시작
    start_date = datetime(2024, 12, 31)
    downloader.fetch_papers(start_date=start_date) 