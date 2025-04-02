import arxiv
import os
import requests
import time
from datetime import datetime, timedelta
from tqdm import tqdm
from pathlib import Path

class ArxivPaperDownloader:
    def __init__(self):
        self.base_dir = Path("data/pdf")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.total_downloaded = 0
        self.total_errors = 0
        
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
    
    def fetch_papers(self, start_date=None, batch_size=1000):
        if start_date is None:
            start_date = datetime(2024, 12, 31)
            
        current_date = start_date
        
        with tqdm(desc="전체 진행률", unit="일") as pbar:
            while True:  # 무한 루프로 변경
                # 검색 쿼리 설정
                categories = ['cs.AI', 'cs.CV']
                query = ' OR '.join(f'cat:{cat}' for cat in categories)
                
                # arXiv API 클라이언트 설정
                client = arxiv.Client()
                
                try:
                    # 한 번에 더 많은 논문을 가져오기
                    search = arxiv.Search(
                        query=query,
                        max_results=batch_size,
                        sort_by=arxiv.SortCriterion.SubmittedDate,
                        sort_order=arxiv.SortOrder.Descending
                    )
                    
                    print(f"\n\n=== {current_date.strftime('%Y-%m-%d')} 이후 논문 검색 중 ===")
                    print(f"검색 쿼리: {query}")
                    
                    # 논문 다운로드
                    papers = list(client.results(search))
                    print(f"검색된 논문 수: {len(papers)}")
                    
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
                    time.sleep(60)
                    continue
                
                print(f"\n=== 진행 상황 ===")
                print(f"총 다운로드: {self.total_downloaded}개")
                print(f"총 실패: {self.total_errors}개")
                
                current_date -= timedelta(days=30)  # 30일씩 과거로 이동
                pbar.update(30)
                time.sleep(3)

if __name__ == "__main__":
    downloader = ArxivPaperDownloader()
    # 2024년 12월 31일부터 과거로 이동
    start_date = datetime(2024, 12, 31)
    downloader.fetch_papers(start_date=start_date) 