import codecs
import datetime
import os

import requests
from fake_useragent import UserAgent
from pyquery import PyQuery as pq

from scripts.core import PlatformReport, TrendItem, TrendSection


# Copied from the project's existing scraper logic and adapted to the skill layout.
DEFAULT_OUTPUT_FOLDER = r"/Users/dock4chips/Documents/dock4chips_vault/trend-intel-skill/github_trend"


def get_headers():
    """获取通用请求头"""
    ua = UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept": "application/vnd.github.v3+json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }


def get_file_path(is_timestamp=False, user_folder=None):
    """获取文件路径，可选是否添加时间戳"""
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    year_month = datetime.datetime.now().strftime("%Y/%m")

    if user_folder is None:
        user_folder = DEFAULT_OUTPUT_FOLDER

    directory = f"{user_folder}/{year_month}"

    if not os.path.exists(directory):
        os.makedirs(directory)

    if is_timestamp:
        time_str = datetime.datetime.now().strftime("%H%M")
        filename = f"{directory}/{date_str}_{time_str}.md"
    else:
        filename = f"{directory}/{date_str}.md"

    return filename, date_str


def check_file_exists(filename):
    """检查文件是否存在，如果存在则添加时间戳"""
    if os.path.exists(filename):
        directory = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        name_parts = os.path.splitext(base_name)
        time_str = datetime.datetime.now().strftime("%H%M")
        new_filename = f"{directory}/{name_parts[0]}_{time_str}{name_parts[1]}"
        return new_filename
    return filename


def create_markdown(date, filename):
    """创建 Markdown 文件并写入标题"""
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    with codecs.open(filename, "w", "utf-8") as file_obj:
        file_obj.write(f"# GitHub 热门榜单 {date} ({current_time})\n\n")
        file_obj.write("## 目录\n\n")
        file_obj.write("- [每日 Star 最多的仓库](#每日-star-最多的仓库)\n")
        file_obj.write("- [每日 Fork 最多的仓库](#每日-fork-最多的仓库)\n")
        file_obj.write("- [每日趋势榜](#每日趋势榜)\n")
        file_obj.write("- [人工智能方向热榜](#人工智能方向热榜)\n")
        file_obj.write("  - [Python](#python)\n\n")


def scrape_trending(language=None):
    """抓取 GitHub 趋势榜"""
    headers = get_headers()

    url = "https://github.com/trending"
    if language:
        url = f"{url}/{language}"

    response = requests.get(url, headers=headers)
    assert response.status_code == 200

    document = pq(response.content)
    items = document("article.Box-row")

    repos = []
    for item in items[:10]:
        current = pq(item)
        title = current("h2 a").text().strip().replace(" ", "")
        owner_repo = current("h2 a").attr("href").strip("/")
        description = current("p").text().strip()
        repo_url = f"https://github.com/{owner_repo}"

        stars_elem = current("div.f6 a[href$='stargazers']")
        stars = stars_elem.text().strip() if stars_elem else "N/A"

        forks_elem = current("div.f6 a[href$='forks']")
        forks = forks_elem.text().strip() if forks_elem else "N/A"

        language_elem = current("div.f6 span[itemprop='programmingLanguage']")
        repo_language = language_elem.text().strip() if language_elem else "N/A"

        repos.append(
            {
                "title": title,
                "url": repo_url,
                "description": description,
                "stars": stars,
                "forks": forks,
                "language": repo_language,
            }
        )

    return repos


def scrape_most_starred():
    """抓取每日 Star 最多的仓库"""
    headers = get_headers()

    try:
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        url = (
            "https://api.github.com/search/repositories"
            f"?q=created:>{one_year_ago}&sort=stars&order=desc&per_page=10"
        )

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "items" not in data:
            print(f"GitHub API 响应异常: {data.get('message', '未知错误')}")
            return []

        repos = []
        for item in data.get("items", [])[:10]:
            repos.append(
                {
                    "title": item["full_name"],
                    "url": item["html_url"],
                    "description": item["description"] or "No description",
                    "stars": str(item["stargazers_count"]),
                    "forks": str(item["forks_count"]),
                    "language": item["language"] or "N/A",
                }
            )

        if not repos:
            print("未获取到任何仓库数据 (Star)")
        return repos
    except requests.exceptions.RequestException as exc:
        print(f"请求 GitHub API 失败 (Star): {str(exc)}")
        return []
    except Exception as exc:
        print(f"处理数据失败 (Star): {str(exc)}")
        return []


def scrape_most_forked():
    """抓取每日 Fork 最多的仓库"""
    headers = get_headers()

    try:
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        url = (
            "https://api.github.com/search/repositories"
            f"?q=pushed:>{one_year_ago}&sort=forks&order=desc&per_page=10"
        )

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "items" not in data:
            print(f"GitHub API 响应异常: {data.get('message', '未知错误')}")
            return []

        repos = []
        for item in data.get("items", [])[:10]:
            repos.append(
                {
                    "title": item["full_name"],
                    "url": item["html_url"],
                    "description": item["description"] or "No description",
                    "stars": str(item["stargazers_count"]),
                    "forks": str(item["forks_count"]),
                    "language": item["language"] or "N/A",
                }
            )

        if not repos:
            print("未获取到任何仓库数据 (Fork)")
        return repos
    except requests.exceptions.RequestException as exc:
        print(f"请求 GitHub API 失败 (Fork): {str(exc)}")
        return []
    except Exception as exc:
        print(f"处理数据失败 (Fork): {str(exc)}")
        return []


def write_repos_to_markdown(filename, section_title, repos, is_subsection=False):
    """将仓库信息以表格方式写入 Markdown 文件"""
    with codecs.open(filename, "a", "utf-8") as file_obj:
        if is_subsection:
            file_obj.write(f"### {section_title}\n\n")
        else:
            file_obj.write(f"## {section_title}\n\n")

        if not repos:
            file_obj.write("*暂无数据*\n\n")
            return

        file_obj.write("| 序号 | 名称 | 描述 | 语言 | Stars | Forks |\n")
        file_obj.write("| --- | --- | --- | --- | --- | --- |\n")

        for index, repo in enumerate(repos):
            description = repo["description"].replace("|", "\\|").replace("\n", " ")
            if len(description) > 100:
                description = description[:97] + "..."

            file_obj.write(
                f"| {index + 1} | [{repo['title']}]({repo['url']}) | "
                f"{description} | {repo['language']} | {repo['stars']} | {repo['forks']} |\n"
            )

        file_obj.write("\n")


def _to_items(repos):
    items = []
    for repo in repos:
        items.append(
            TrendItem(
                title=repo["title"],
                url=repo["url"],
                description=repo["description"],
                language=repo["language"],
                stars=repo["stars"],
                forks=repo["forks"],
            )
        )
    return items


def collect(output_dir=None, use_timestamp=False):
    """抓取 GitHub 数据并生成标准 Skill 报告"""
    filename, date = get_file_path(use_timestamp, output_dir)
    filename = check_file_exists(filename)

    create_markdown(date, filename)

    star_repos = scrape_most_starred()
    write_repos_to_markdown(filename, "每日 Star 最多的仓库", star_repos)

    fork_repos = scrape_most_forked()
    write_repos_to_markdown(filename, "每日 Fork 最多的仓库", fork_repos)

    trending_repos = scrape_trending()
    write_repos_to_markdown(filename, "每日趋势榜", trending_repos)

    write_repos_to_markdown(filename, "人工智能方向热榜", [], is_subsection=False)

    python_repos = scrape_trending("python")
    write_repos_to_markdown(filename, "Python", python_repos, is_subsection=True)

    return PlatformReport(
        platform="github",
        filename=filename,
        date=date,
        sections=[
            TrendSection(title="每日 Star 最多的仓库", items=_to_items(star_repos)),
            TrendSection(title="每日 Fork 最多的仓库", items=_to_items(fork_repos)),
            TrendSection(title="每日趋势榜", items=_to_items(trending_repos)),
            TrendSection(title="人工智能方向热榜", items=[]),
            TrendSection(title="Python", items=_to_items(python_repos), is_subsection=True),
        ],
    )
