from __future__ import annotations
import sqlite3, os
from pathlib import Path
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP=None
from app.services.query import crm_query
from app.services.briefing import person_brief
DB=os.getenv('RELATIONSHIPOS_DB',str(Path(__file__).resolve().parents[1]/'relationshipos.db'))
def con():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
if FastMCP:
 mcp=FastMCP('RelationshipOS')
 @mcp.tool()
 def search_relationships(query:str)->dict:
  c=con(); x=crm_query(c,query); c.close(); return x
 @mcp.tool()
 def person_context(person_id:int)->dict:
  c=con(); x=person_brief(c,person_id) or {}; c.close(); return x
if __name__=='__main__':
 if not FastMCP: raise SystemExit('Install mcp package')
 mcp.run()
