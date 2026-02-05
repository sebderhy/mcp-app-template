/**
 * Todo List Widget Template
 *
 * Interactive todo list with drag-and-drop - perfect for:
 * - Task management
 * - Checklists
 * - Project tracking
 * - Shopping lists
 */

import React, { useRef, useState, useEffect, useMemo, forwardRef } from "react";
import {
  AnimatePresence,
  motion,
  Reorder,
  useDragControls,
} from "framer-motion";
import { List, GripVertical, Plus, Calendar, EllipsisVertical, Trash2 } from "lucide-react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useWidgetProps } from "../use-widget-props";
import { useWidgetState } from "../use-widget-state";

type TodoItem = {
  id: string;
  title: string;
  isComplete: boolean;
  note?: string;
  dueDate?: string | null;
};

type TodoList = {
  id: string;
  title: string;
  isCurrentlyOpen?: boolean;
  todos: TodoItem[];
};

type ToolOutput = {
  lists: TodoList[];
};

type WidgetState = {
  lists: TodoList[];
  currentListId: string | null;
  currentListTitle: string | null;
};

const defaultProps: ToolOutput = {
  lists: [
    {
      id: "work",
      title: "Work Tasks",
      isCurrentlyOpen: true,
      todos: [
        { id: "1", title: "Review pull requests", isComplete: false, note: "Check the new feature branch" },
        { id: "2", title: "Update documentation", isComplete: true },
        { id: "3", title: "Team standup meeting", isComplete: false, dueDate: "2025-01-15" },
      ],
    },
    {
      id: "personal",
      title: "Personal",
      todos: [
        { id: "4", title: "Buy groceries", isComplete: false },
        { id: "5", title: "Call mom", isComplete: false, dueDate: "2025-01-14" },
      ],
    },
    {
      id: "shopping",
      title: "Shopping List",
      todos: [
        { id: "6", title: "Milk", isComplete: false },
        { id: "7", title: "Bread", isComplete: true },
        { id: "8", title: "Eggs", isComplete: false },
      ],
    },
  ],
};

const DEFAULT_LIST_TITLE = "Untitled List";

/* --------------------------------- Utils -------------------------------- */
function uid() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return (Date.now().toString(36) + Math.random().toString(36).slice(2, 10)).toUpperCase();
}

function formatDueDate(d: string | null | undefined) {
  if (!d) return "";
  const parts = d.split("-");
  if (parts.length !== 3) return "";
  const y = parseInt(parts[0], 10);
  const m = parseInt(parts[1], 10);
  const day = parseInt(parts[2], 10);
  const dt = new Date(y, (m || 1) - 1, day || 1);
  const now = new Date();
  const sameYear = dt.getFullYear() === now.getFullYear();
  const opts: Intl.DateTimeFormatOptions = sameYear
    ? { month: "short", day: "numeric" }
    : { month: "short", day: "numeric", year: "numeric" };
  return dt.toLocaleDateString(undefined, opts);
}

function parseYMD(s: string | null | undefined): Date | null {
  if (!s || typeof s !== "string") return null;
  const [y, m, d] = s.split("-").map((v) => parseInt(v, 10));
  if (!y || !m || !d) return null;
  return new Date(y, m - 1, d);
}

function toYMD(date: Date | null): string | null {
  if (!(date instanceof Date) || isNaN(date.getTime())) return null;
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function useClickOutside(ref: React.RefObject<HTMLElement>, handler: () => void) {
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) handler();
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [ref, handler]);
}

function getRelativePosition(element: DOMRect, target: DOMRect) {
  return {
    left: element.left - target.left,
    top: element.top - target.top,
    width: element.width,
    height: element.height,
  };
}

/* -------------------------- Circular checkbox --------------------------- */
function CircleCheckbox({ checked, onToggle, label }: { checked: boolean; onToggle: () => void; label: string }) {
  return (
    <div
      role="checkbox"
      aria-checked={checked}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === " " || e.key === "Enter") {
          e.preventDefault();
          onToggle();
        }
      }}
      onClick={(e) => {
        e.stopPropagation();
        onToggle();
      }}
      className="w-4 h-4 rounded-full border flex items-center justify-center cursor-pointer select-none outline-none border-gray-400 focus-visible:ring-2 focus-visible:ring-black/20"
      aria-label={label}
    >
      <AnimatePresence initial={false}>
        {checked && (
          <motion.div
            key="dot"
            initial={{ scale: 0.6, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.6, opacity: 0 }}
            transition={{ type: "spring", bounce: 0.3, duration: 0.28 }}
            className="rounded-full bg-black w-[11.5px] h-[11.5px]"
          />
        )}
      </AnimatePresence>
    </div>
  );
}

/* --------------------------------- BaseCard -------------------------------- */
function BaseCard({ children }: { children: React.ReactNode }) {
  return (
    <motion.div className="absolute inset-0 bg-gray-50/100 rounded-2xl sm:rounded-3xl border border-black/10 shadow-[0px_8px_14px_rgba(0,0,0,0.05)] overflow-hidden">
      {children}
    </motion.div>
  );
}

/* ===================== Details Section ===================== */
function DetailsSection({
  isOpen,
  item,
  updateItemById,
  noteRef,
  autoFocusNote,
  onClickInside,
}: {
  isOpen: boolean;
  item: TodoItem;
  updateItemById: (id: string, val: Partial<TodoItem>) => void;
  noteRef: React.RefObject<HTMLInputElement>;
  autoFocusNote: boolean;
  onClickInside?: () => void;
}) {
  return (
    <AnimatePresence initial={false}>
      {isOpen && (
        <motion.div
          key="details"
          initial={{ height: 0 }}
          animate={{ height: "auto" }}
          exit={{ height: 0 }}
          transition={{ type: "spring", bounce: 0.24, duration: 0.35 }}
          className="overflow-hidden"
          layout
        >
          <div
            className="px-4 sm:px-8 pb-3.5 pt-0 flex flex-col gap-2 text-sm"
            onClick={(e) => {
              e.stopPropagation();
              onClickInside?.();
            }}
          >
            <input
              ref={noteRef}
              autoFocus={autoFocusNote}
              value={item.note ?? ""}
              onChange={(e) => updateItemById(item.id, { note: e.target.value })}
              placeholder="Add Note"
              className="w-full bg-transparent outline-none border-0 focus:ring-0 focus-visible:ring-0 text-sm text-black/55 placeholder-black/30"
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ============================= Item row ============================= */
function TodoListItem({
  item,
  index,
  isNew,
  updateItemById,
  deleteTodoById,
}: {
  item: TodoItem;
  index: number;
  isNew: boolean;
  updateItemById: (id: string, val: Partial<TodoItem>) => void;
  deleteTodoById: (id: string) => void;
}) {
  const controls = useDragControls();
  const [isFocused, setIsFocused] = useState(isNew ?? false);
  const [isHovered, setIsHovered] = useState(false);
  const [focusTarget, setFocusTarget] = useState<string | null>(isNew ? "title" : null);
  const [menuOpen, setMenuOpen] = useState(false);

  const dragStartedRef = useRef(false);
  const pointerDownPosRef = useRef<{ x: number; y: number } | null>(null);
  const POINTER_THRESHOLD = 4;

  const containerRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLInputElement>(null);
  const noteRef = useRef<HTMLInputElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const datepickerRef = useRef<any>(null);

  useClickOutside(containerRef, () => {
    setIsFocused(false);
    setFocusTarget(null);
    setMenuOpen(false);
  });

  useEffect(() => {
    if (!isFocused) return;
    if (focusTarget === "title" && titleRef.current) titleRef.current.focus();
    if (focusTarget === "note" && noteRef.current) noteRef.current.focus();
  }, [isFocused, focusTarget]);

  const hasNote = (item.note ?? "").length > 0;
  const detailsOpen = isFocused || hasNote;

  const dateLabel = formatDueDate(item.dueDate);
  const selectedDate = parseYMD(item.dueDate);

  const openReactDatePicker = () => {
    try {
      datepickerRef.current?.setOpen(true);
    } catch {}
  };

  const portalId = useMemo(() => `dp-portal-${item.id}`, [item.id]);

  const HiddenAnchorInput = forwardRef<HTMLInputElement, any>(function HiddenAnchorInput(props, ref) {
    return (
      <input
        {...props}
        ref={ref}
        className="absolute top-full left-0 w-[1px] h-[1px] opacity-0 pointer-events-none"
        aria-hidden
        tabIndex={-1}
      />
    );
  });

  const onEllipsisPointerDown = (e: React.PointerEvent) => {
    e.stopPropagation();
    e.currentTarget.setPointerCapture?.(e.pointerId);
    pointerDownPosRef.current = { x: e.clientX, y: e.clientY };
    dragStartedRef.current = false;
  };

  const onEllipsisPointerMove = (e: React.PointerEvent) => {
    if (!pointerDownPosRef.current || dragStartedRef.current) return;
    const dx = e.clientX - pointerDownPosRef.current.x;
    const dy = e.clientY - pointerDownPosRef.current.y;
    if (Math.hypot(dx, dy) >= POINTER_THRESHOLD) {
      dragStartedRef.current = true;
      setMenuOpen(false);
      controls.start(e as any);
    }
  };

  const endPointerCycle = (e: React.PointerEvent) => {
    pointerDownPosRef.current = null;
    dragStartedRef.current = false;
    e.currentTarget.releasePointerCapture?.(e.pointerId);
  };

  const onEllipsisPointerUp = (e: React.PointerEvent) => {
    e.stopPropagation();
    if (!dragStartedRef.current) {
      setMenuOpen((o) => !o);
    }
    endPointerCycle(e);
  };

  return (
    <Reorder.Item
      value={item.id}
      id={item.id}
      key={item.id}
      ref={containerRef}
      as="div"
      dragListener={false}
      dragControls={controls}
      className="relative"
      layout="position"
      initial={false}
    >
      <motion.div
        layout
        initial={isNew ? { opacity: 0, y: 18, scale: 0.98 } : false}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, filter: "blur(4px)", scale: 0.98 }}
        transition={{ type: "spring", bounce: 0.18, duration: 0.42 }}
        className="border-b border-black/5 bg-white"
      >
        <div
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          className="flex gap-3 py-3 items-center"
          onClick={() => {
            setIsFocused(true);
            setFocusTarget("title");
          }}
        >
          <CircleCheckbox
            checked={!!item.isComplete}
            onToggle={() => updateItemById(item.id, { isComplete: !item.isComplete })}
            label={item.title || "Todo"}
          />

          <input
            ref={titleRef}
            onClick={(e) => {
              e.stopPropagation();
              setIsFocused(true);
              setFocusTarget("title");
            }}
            onChange={(e) => updateItemById(item.id, { title: e.target.value })}
            placeholder="Add a to-do"
            className={`leading-tight flex-auto border-transparent border-0 bg-transparent !text-base p-0 outline-none focus-visible:ring-0 ${
              item.isComplete ? "line-through text-black/40" : ""
            }`}
            value={item.title}
          />

          <div
            className="relative shrink-0 flex items-center gap-0.5"
            onClick={(e) => e.stopPropagation()}
          >
            {!dateLabel && (
              <motion.button
                type="button"
                animate={{ opacity: isHovered ? 1 : 0 }}
                onClick={openReactDatePicker}
                aria-label="Edit due date"
                className="p-1 rounded-md hover:bg-black/5"
              >
                <Calendar className="w-4 h-4 text-black/40" />
              </motion.button>
            )}

            {dateLabel && (
              <button
                type="button"
                onClick={openReactDatePicker}
                aria-label={`Edit due date ${dateLabel}`}
                className="text-sm text-black/40 hover:text-black/70 rounded-md"
              >
                {dateLabel}
              </button>
            )}

            <div id={portalId} className="absolute left-0 top-full mt-1 z-[70]" />

            <DatePicker
              ref={datepickerRef}
              selected={selectedDate}
              onChange={(date) => {
                const ymd = toYMD(date);
                updateItemById(item.id, { dueDate: ymd });
              }}
              dateFormat="yyyy-MM-dd"
              customInput={<HiddenAnchorInput />}
              shouldCloseOnSelect
              showPopperArrow={false}
              popperPlacement="bottom-start"
              portalId={portalId}
              onClickOutside={() => datepickerRef.current?.setOpen(false)}
            />
          </div>

          <div
            className="relative shrink-0 w-2 flex items-center justify-center"
            onClick={(e) => e.stopPropagation()}
          >
            <motion.button
              type="button"
              aria-label="More actions"
              aria-haspopup="menu"
              aria-expanded={menuOpen}
              className="p-1 rounded-md select-none text-black/30 hover:text-black cursor-pointer"
              style={{ touchAction: "none" }}
              animate={{ opacity: isHovered ? 1 : 0 }}
              onPointerDown={onEllipsisPointerDown}
              onPointerMove={onEllipsisPointerMove}
              onPointerUp={onEllipsisPointerUp}
              onPointerCancel={endPointerCycle}
            >
              <EllipsisVertical className="w-4 h-4" />
            </motion.button>

            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  ref={menuRef}
                  initial={{ opacity: 0, scale: 0.98, y: -2 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.98, y: -2 }}
                  transition={{ type: "spring", bounce: 0.2, duration: 0.18 }}
                  className="absolute right-0 top-full mt-1 min-w-[120px] rounded-md border border-black/10 bg-white shadow-md z-20"
                  role="menu"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    role="menuitem"
                    className="w-full text-left text-sm px-3 py-2 hover:bg-black/5"
                    onClick={() => {
                      setMenuOpen(false);
                      deleteTodoById(item.id);
                    }}
                  >
                    Delete
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        <DetailsSection
          isOpen={detailsOpen}
          item={item}
          updateItemById={updateItemById}
          noteRef={noteRef}
          autoFocusNote={isFocused && focusTarget === "note"}
          onClickInside={() => {
            setIsFocused(true);
            setFocusTarget("note");
          }}
        />
      </motion.div>
    </Reorder.Item>
  );
}

/* ============================= List detail ============================= */
function TodoListDetail({
  list,
  items,
  setItemsByOrder,
  updateItemById,
  deleteItemById,
  updateListById,
  recentlyAddedId,
}: {
  list: TodoList;
  items: TodoItem[];
  setItemsByOrder: (ids: string[]) => void;
  updateItemById: (id: string, val: Partial<TodoItem>) => void;
  deleteItemById: (id: string) => void;
  updateListById: (listId: string, val: Partial<TodoList>) => void;
  recentlyAddedId: string | null;
}) {
  const titleInputRef = useRef<HTMLInputElement>(null);
  const [titleDraft, setTitleDraft] = useState(list.title ?? "");

  useEffect(() => {
    setTitleDraft(list.title ?? "");
  }, [list.id, list.title]);

  const commitTitle = () => {
    const trimmed = titleDraft.trim();
    const nextTitle = trimmed.length > 0 ? trimmed : DEFAULT_LIST_TITLE;
    if (nextTitle !== titleDraft) {
      setTitleDraft(nextTitle);
    }
    if ((list.title ?? "") !== nextTitle) {
      updateListById(list.id, { title: nextTitle });
    }
  };

  const handleTitleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      commitTitle();
      titleInputRef.current?.blur();
    } else if (e.key === "Escape") {
      e.preventDefault();
      setTitleDraft(list.title ?? "");
      titleInputRef.current?.blur();
    }
  };

  const itemIds = useMemo(() => items.map((t) => t.id), [items]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { duration: 0 } }}
      exit={{ opacity: 0, transition: { delay: 0.24, duration: 0.24 } }}
      transition={{ type: "spring", bounce: 0.16, duration: 0.56 }}
      className="bg-white w-full h-full overflow-auto"
      layout
    >
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ type: "spring", bounce: 0.16, duration: 0.56 }}
        className="w-full flex top-0 left-0 absolute h-14 bg-white z-10"
      />
      <motion.div
        initial={{ scale: 1, y: 0, fontWeight: 500 }}
        animate={{ scale: 1.5, y: 40, fontWeight: 500 }}
        exit={{ scale: 1, y: 0, fontWeight: 500 }}
        transition={{ type: "spring", bounce: 0.16, duration: 0.56 }}
        className="text-md tracking-tight m-3 sm:m-5 origin-top-left"
      >
        <input
          ref={titleInputRef}
          type="text"
          value={titleDraft}
          onChange={(e) => setTitleDraft(e.target.value)}
          onBlur={commitTitle}
          onKeyDown={handleTitleKeyDown}
          placeholder={DEFAULT_LIST_TITLE}
          className="w-full bg-transparent border-0 outline-none focus:ring-0 focus-visible:ring-0 p-0 m-0 text-inherit"
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1, transition: { duration: 0 } }}
        exit={{ opacity: 0 }}
        transition={{ type: "spring", bounce: 0.16, duration: 0.56 }}
        className="p-3 sm:p-5 mt-10 flex flex-col"
        layout
      >
        <Reorder.Group
          as="div"
          axis="y"
          values={itemIds}
          onReorder={setItemsByOrder}
        >
          <AnimatePresence initial={false}>
            {items.map((item, i) => (
              <TodoListItem
                key={item.id}
                index={i}
                item={item}
                isNew={recentlyAddedId === item.id}
                updateItemById={updateItemById}
                deleteTodoById={deleteItemById}
              />
            ))}
          </AnimatePresence>
        </Reorder.Group>
      </motion.div>
    </motion.div>
  );
}

/* ============================ Zoom container ============================ */
function ZoomViewer({
  origin,
  containerRef,
  children,
}: {
  origin: React.RefObject<HTMLElement>;
  containerRef: React.RefObject<HTMLElement>;
  children: React.ReactNode;
}) {
  const originRect = getRelativePosition(
    origin.current!.getBoundingClientRect(),
    containerRef.current!.getBoundingClientRect()
  );
  const initial = {
    left: originRect.left,
    top: originRect.top,
    width: originRect.width,
    height: originRect.height,
  };
  const animate = { left: 0, top: 0, width: "100%", height: "100%" };
  return (
    <motion.div
      initial={initial}
      animate={animate}
      exit={initial}
      transition={{ type: "spring", bounce: 0.16, duration: 0.56 }}
      className="absolute overflow-hidden w-full h-full"
    >
      {children}
    </motion.div>
  );
}

/* Shows a list row */
function TodoListGroup({
  index,
  title,
  todoCount,
  isExpanded,
  setCurrentTodoList,
  onDelete,
  registerRowRef,
}: {
  index: number;
  title: string;
  todoCount: number;
  isExpanded: boolean;
  containerRef: React.RefObject<HTMLElement>;
  setCurrentTodoList: (ref: React.RefObject<HTMLDivElement>, index: number) => void;
  onDelete: (index: number) => void;
  registerRowRef: (index: number, ref: React.RefObject<HTMLDivElement>) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState<number | "auto">("auto");
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (ref.current) setHeight(ref.current.getBoundingClientRect().height);
    registerRowRef(index, ref);
  }, [index, registerRowRef]);

  return (
    <motion.div animate={{ height: isExpanded ? "100%" : height }}>
      <div
        ref={ref}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="p-3 sm:p-5 text-md cursor-pointer hover:bg-white/40 border-b border-black/10 flex items-center gap-3"
        onClick={() => setCurrentTodoList(ref, index)}
      >
        <div className="flex-1">
          <div className="font-medium">{title}</div>
          <div className="text-sm text-black/50">{todoCount} items</div>
        </div>
        <motion.div animate={{ opacity: isHovered ? 1 : 0 }}>
          <Trash2
            className="w-4 h-4 text-black/30 hover:text-black cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(index);
            }}
          />
        </motion.div>
      </div>
    </motion.div>
  );
}

/* ================================ App =================================== */
export default function App() {
  const ref = useRef<HTMLDivElement>(null);
  const props = useWidgetProps<ToolOutput>(defaultProps);

  const initialOpenList = props.lists.find((l) => l.isCurrentlyOpen);
  const [widgetState, setWidgetState] = useWidgetState<WidgetState>({
    lists: props.lists,
    currentListId: initialOpenList?.id ?? null,
    currentListTitle: initialOpenList?.title ?? null,
  });

  const data = widgetState ?? { lists: props.lists };

  const initialOpenIndex = useMemo(() => {
    const idx = (data.lists || []).findIndex((l) => l.isCurrentlyOpen);
    return idx >= 0 ? idx : null;
  }, []);

  const [currentTodoListRef, setCurrentTodoListRef] = useState<React.RefObject<HTMLDivElement> | null>(null);
  const [currentTodoList, setCurrentTodoList] = useState<number | null>(initialOpenIndex);
  const [recentlyAddedId, setRecentlyAddedId] = useState<string | null>(null);
  const [rowRefs, setRowRefs] = useState<Record<number, React.RefObject<HTMLDivElement>>>({});

  const registerRowRef = (index: number, rowRef: React.RefObject<HTMLDivElement>) => {
    setRowRefs((prev) => ({ ...prev, [index]: rowRef }));
  };

  useEffect(() => {
    if (currentTodoList != null && !currentTodoListRef) {
      const r = rowRefs[currentTodoList];
      if (r && r.current) {
        setCurrentTodoListRef(r);
      }
    }
  }, [currentTodoList, currentTodoListRef, rowRefs]);

  const todoLists = data.lists;
  const currentList = currentTodoList != null ? todoLists[currentTodoList] : null;
  const currentItems = currentList ? currentList.todos : [];

  const updateData = (newLists: TodoList[], listId?: string | null, listTitle?: string | null) => {
    setWidgetState((prev) => ({
      lists: newLists,
      currentListId: listId !== undefined ? listId : (prev?.currentListId ?? null),
      currentListTitle: listTitle !== undefined ? listTitle : (prev?.currentListTitle ?? null),
    }));
  };

  const addList = () => {
    const newLists = [{ id: uid(), title: "New List", isCurrentlyOpen: false, todos: [] }, ...data.lists];
    updateData(newLists);
    setCurrentTodoList((idx) => (idx == null ? idx : idx + 1));
  };

  const deleteList = (listIndex: number) => {
    const lists = data.lists.slice();
    lists.splice(listIndex, 1);
    updateData(lists);
    setCurrentTodoList((idx) => {
      if (idx == null) return idx;
      if (idx === listIndex) {
        setCurrentTodoListRef(null);
        return null;
      }
      if (idx > listIndex) return idx - 1;
      return idx;
    });
  };

  const openList = (r: React.RefObject<HTMLDivElement> | null, index: number) => {
    setCurrentTodoListRef(r);
    setCurrentTodoList(index);
    const targetList = data.lists[index];
    const lists = data.lists.map((l, i) => ({ ...l, isCurrentlyOpen: i === index }));
    updateData(lists, targetList?.id ?? null, targetList?.title ?? null);
  };

  const updateListById = (listId: string, val: Partial<TodoList>) => {
    const lists = data.lists.map((l) => (l.id === listId ? { ...l, ...val } : l));
    updateData(lists);
  };

  const addTodo = () => {
    if (currentList == null || currentTodoList == null) return;
    const newId = uid();
    setRecentlyAddedId(newId);
    setTimeout(() => setRecentlyAddedId(null), 600);

    const lists = data.lists.slice();
    const list = { ...lists[currentTodoList] };
    list.todos = [
      { id: newId, title: "", isComplete: false, note: "", dueDate: null },
      ...list.todos,
    ];
    lists[currentTodoList] = list;
    updateData(lists);
  };

  const deleteItemById = (id: string) => {
    if (currentList == null || currentTodoList == null) return;
    const lists = data.lists.slice();
    const list = { ...lists[currentTodoList] };
    list.todos = list.todos.filter((t) => t.id !== id);
    lists[currentTodoList] = list;
    updateData(lists);
  };

  const setItemsByOrder = (orderedIds: string[]) => {
    if (currentList == null || currentTodoList == null) return;
    const lists = data.lists.slice();
    const list = { ...lists[currentTodoList] };
    const byId = new Map(list.todos.map((t) => [t.id, t]));
    list.todos = orderedIds.map((id) => byId.get(id)).filter(Boolean) as TodoItem[];
    lists[currentTodoList] = list;
    updateData(lists);
  };

  const updateItemById = (id: string, val: Partial<TodoItem>) => {
    if (currentList == null || currentTodoList == null) return;
    const lists = data.lists.slice();
    const list = { ...lists[currentTodoList] };
    list.todos = list.todos.map((t) => (t.id === id ? { ...t, ...val } : t));
    lists[currentTodoList] = list;
    updateData(lists);
  };

  return (
    <div className="antialiased flex items-center justify-center w-full h-full min-h-[400px] p-2 sm:p-4">
      <div
        className="relative w-full h-full max-w-md sm:max-w-[28rem] min-h-[400px] sm:min-h-[31rem]"
      >
        <BaseCard>
          <div ref={ref} className="w-full h-full pt-9">
            <div className="w-full flex top-0 left-0 absolute p-3 sm:p-5 z-20">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: currentList ? 1 : 0 }}
                transition={{ type: "spring", bounce: 0.16, duration: 0.56 }}
              >
                <List
                  size={20}
                  onClick={() => {
                    setCurrentTodoList(null);
                    setCurrentTodoListRef(null);
                    const lists = data.lists.map((l) => ({ ...l, isCurrentlyOpen: false }));
                    updateData(lists, null, null);
                  }}
                  className="cursor-pointer"
                />
              </motion.div>
              <div className="flex-auto" />
              <Plus size={20} onClick={currentList ? addTodo : addList} className="cursor-pointer" />
            </div>

            <motion.div
              animate={{
                opacity: currentList ? 0 : 1,
                filter: currentList ? "blur(8px)" : "blur(0px)",
              }}
              transition={{ type: "spring", bounce: 0.16, duration: 0.56 }}
              className="w-full h-full"
            >
              <div className="p-3 sm:p-5">
                <h1 className="font-medium text-xl sm:text-2xl tracking-tight">My Lists</h1>
              </div>
              {todoLists.map((list, idx) => (
                <TodoListGroup
                  key={list.id}
                  index={idx}
                  title={list.title}
                  todoCount={list.todos.length}
                  isExpanded={idx === currentTodoList}
                  containerRef={ref}
                  setCurrentTodoList={openList}
                  onDelete={deleteList}
                  registerRowRef={registerRowRef}
                />
              ))}
            </motion.div>

            <AnimatePresence mode="popLayout">
              {currentList != null && (
                currentTodoListRef ? (
                  <ZoomViewer origin={currentTodoListRef} containerRef={ref}>
                    <TodoListDetail
                      list={currentList}
                      items={currentItems}
                      setItemsByOrder={setItemsByOrder}
                      updateItemById={updateItemById}
                      deleteItemById={deleteItemById}
                      updateListById={updateListById}
                      recentlyAddedId={recentlyAddedId}
                    />
                  </ZoomViewer>
                ) : (
                  <motion.div
                    key="direct-detail"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0"
                  >
                    <TodoListDetail
                      list={currentList}
                      items={currentItems}
                      setItemsByOrder={setItemsByOrder}
                      updateItemById={updateItemById}
                      deleteItemById={deleteItemById}
                      updateListById={updateListById}
                      recentlyAddedId={recentlyAddedId}
                    />
                  </motion.div>
                )
              )}
            </AnimatePresence>
          </div>
        </BaseCard>
      </div>
    </div>
  );
}
